import os
import json
import time
import hashlib
import random
import httpx
import structlog
from jose import jwt

logger = structlog.get_logger()


class EmbeddingClient:
    """
    Unified client for generating text embeddings (1536 dimensions).
    Supports multiple providers (vertex_ai, openai, mock) dynamically
    configured via environment variables.
    """

    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER", "mock").lower()
        self.gcp_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        self.gcp_location = os.getenv("GCP_LOCATION", "us-central1")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # OAuth2 Token Cache for Vertex AI
        self._token = None
        self._token_expires_at = 0

    def _generate_mock_embedding(self, text: str) -> list[float]:
        """
        Generates a deterministic 1536-dimensional mock vector.
        Normalized to unit length for mathematical validity in cosine similarity.
        """
        hasher = hashlib.sha256(text.encode("utf-8"))
        seed = int(hasher.hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        vector = [rng.uniform(-1, 1) for _ in range(1536)]
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        return vector

    async def _get_vertex_ai_token(self) -> str:
        """
        Exchanges a signed JWT assertion for a Google OAuth2 access token.
        Caches the token until it expires.
        """
        now = int(time.time())
        # If cached token is still valid for at least 5 minutes, use it
        if self._token and self._token_expires_at > now + 300:
            return self._token

        if not self.gcp_credentials_path or not os.path.exists(
            self.gcp_credentials_path
        ):
            raise ValueError(
                f"GCP credentials file not found at: {self.gcp_credentials_path}"
            )

        with open(self.gcp_credentials_path, "r") as f:
            creds = json.load(f)

        client_email = creds["client_email"]
        private_key = creds["private_key"]
        token_uri = creds.get("token_uri", "https://oauth2.googleapis.com/token")

        payload = {
            "iss": client_email,
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "aud": token_uri,
            "exp": now + 3600,
            "iat": now,
        }

        assertion = jwt.encode(payload, private_key, algorithm="RS256")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_uri,
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": assertion,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            self._token = data["access_token"]
            self._token_expires_at = now + int(data.get("expires_in", 3600))
            return self._token

    async def _get_vertex_embedding(self, text: str) -> list[float]:
        """
        Calls Vertex AI text-embedding-004 model (768 dim) and pads it to 1536 dim.
        """
        token = await self._get_vertex_ai_token()

        project_id = self.gcp_project_id
        if (
            not project_id
            and self.gcp_credentials_path
            and os.path.exists(self.gcp_credentials_path)
        ):
            with open(self.gcp_credentials_path, "r") as f:
                creds = json.load(f)
                project_id = creds.get("project_id")

        if not project_id:
            raise ValueError("GCP Project ID is missing")

        url = f"https://{self.gcp_location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{self.gcp_location}/publishers/google/models/text-embedding-004:predict"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "instances": [
                {
                    "content": text,
                    "taskType": "RETRIEVAL_DOCUMENT",
                }
            ],
            "parameters": {
                "outputDimensionality": 768,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=headers, json=payload, timeout=20.0
            )
            response.raise_for_status()

            predictions = response.json().get("predictions", [])
            if not predictions:
                raise ValueError("Vertex AI returned an empty response")

            raw_vector = predictions[0]["embeddings"]["values"]

            # Zero-padding from 768 to 1536 elements
            if len(raw_vector) < 1536:
                raw_vector = raw_vector + [0.0] * (1536 - len(raw_vector))
            return raw_vector

    async def _get_openai_embedding(self, text: str) -> list[float]:
        """
        Calls OpenAI API text-embedding-3-small (1536 dim).
        """
        if not self.openai_key or self.openai_key.startswith("sk-..."):
            raise ValueError("Invalid OpenAI API Key")

        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": text,
            "model": "text-embedding-3-small",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=headers, json=payload, timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def get_embedding(self, text: str) -> list[float]:
        """
        Generates a 1536-dimensional embedding vector for the given text.
        Falls back to mock embeddings if errors occur or key is placeholder.
        """
        if not text or not text.strip():
            return [0.0] * 1536

        # Force mock provider if keys are placeholders or not configured
        if self.provider == "vertex_ai":
            if (
                not self.gcp_credentials_path
                or self.gcp_credentials_path.startswith("path/to")
                or not os.path.exists(self.gcp_credentials_path)
            ):
                logger.warning(
                    "vertex_ai_credentials_not_found_falling_back_to_mock",
                    path=self.gcp_credentials_path,
                )
                return self._generate_mock_embedding(text)
        elif self.provider == "openai":
            if not self.openai_key or self.openai_key.startswith("sk-..."):
                logger.warning("openai_key_not_configured_falling_back_to_mock")
                return self._generate_mock_embedding(text)

        try:
            if self.provider == "vertex_ai":
                return await self._get_vertex_embedding(text)
            elif self.provider == "openai":
                return await self._get_openai_embedding(text)
            else:
                return self._generate_mock_embedding(text)
        except Exception as e:
            logger.error(
                "embedding_generation_failed_falling_back_to_mock",
                provider=self.provider,
                error=str(e),
            )
            return self._generate_mock_embedding(text)


# Singleton instance
embedding_client = EmbeddingClient()
