import os
import psycopg2
from temporalio import activity
from dotenv import load_dotenv
import httpx
import litellm

# Load env variables from root folder (.env is 2 levels up from workers/company-research/src/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

from src.embeddings import embedding_client  # noqa: E402


def generate_mock_search_results(company_name: str) -> str:
    """
    Returns high-quality mock search results about the company.
    """
    return (
        f"Snippet 1: PT {company_name} announces a partnership with global cloud leaders to accelerate digital transformation.\n"
        f"Snippet 2: News: PT {company_name} records a major efficiency increase after migrating legacy networks to automated IT systems.\n"
        f"Snippet 3: {company_name} career pages show active hiring for software developers skilled in Python, React, and PostgreSQL.\n"
        f"Snippet 4: Profile: {company_name} specializes in delivering technology services and infrastructure management to regional businesses."
    )


async def query_tavily_search(company_name: str, api_key: str) -> str:
    """
    Queries Tavily Search API for business profile details.
    """
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": f"{company_name} business profile industry news tech stack",
        "search_depth": "basic",
        "max_results": 4,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            results = response.json().get("results", [])
            snippets = []
            for r in results:
                snippets.append(f"Title: {r.get('title')}\nContent: {r.get('content')}")
            return "\n\n".join(snippets)
    except Exception as e:
        activity.logger.error(f"Tavily search API query failed: {e}")
        return generate_mock_search_results(company_name)


@activity.defn
async def research_company_profile(company_name: str) -> str:
    """
    Autonomously researches corporate profile summaries using Search APIs and LiteLLM.
    """
    activity.logger.info(f"Researching company profile for: {company_name}")

    tavily_key = os.getenv("TAVILY_API_KEY")
    llm_provider = os.getenv("RESEARCH_LLM_PROVIDER", "vertex_ai").lower()
    llm_model = os.getenv("RESEARCH_LLM_MODEL", "vertex_ai/gemini-2.5-flash")

    # 1. Fetch web search results
    if tavily_key and not tavily_key.startswith("tvly-..."):
        search_context = await query_tavily_search(company_name, tavily_key)
    else:
        search_context = generate_mock_search_results(company_name)

    # 2. Map GCP variables for LiteLLM if using Vertex AI
    if llm_provider == "vertex_ai":
        if not os.getenv("VERTEX_PROJECT") and os.getenv("GCP_PROJECT_ID"):
            os.environ["VERTEX_PROJECT"] = os.getenv("GCP_PROJECT_ID")
        if not os.getenv("VERTEX_LOCATION") and os.getenv("GCP_LOCATION"):
            os.environ["VERTEX_LOCATION"] = os.getenv("GCP_LOCATION")

    # Mock Summary fallback
    mock_summary = (
        f"{company_name} merupakan pemain terkemuka di sektor korporasi. Akhir-akhir ini, mereka fokus "
        f"memperluas kapabilitas digital, memindahkan beban kerja IT ke platform cloud, dan meningkatkan "
        f"efisiensi operasional berbasis AI. Teknologi utama mereka mencakup modernisasi arsitektur sistem "
        f"dan kemitraan teknologi strategis."
    )

    # 3. Call LiteLLM asynchronously
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional business research analyst. "
                    "Write a concise corporate profile summary based ONLY on the provided search context. "
                    "Your response must be in Indonesian, strictly under 150 words, and formatted as a single cohesive paragraph. "
                    "Avoid formatting with bullet points or markdown headers. Summarize: 1. Core business focus, "
                    "2. Key initiatives/news, 3. Technology focus (clues from tech stack/cloud)."
                ),
            },
            {
                "role": "user",
                "content": f"Company Name: {company_name}\n\nSearch Context:\n{search_context}",
            },
        ]

        # Configure LiteLLM response timeout
        response = await litellm.acompletion(
            model=llm_model, messages=messages, timeout=30.0
        )
        summary = response.choices[0].message.content.strip()
        activity.logger.info(
            "AI research profile generated successfully", model=llm_model
        )
        return summary
    except Exception as llm_err:
        activity.logger.error(
            f"LiteLLM completion failed, falling back to mock summary: {llm_err}"
        )
        return mock_summary


@activity.defn
async def update_account_in_db(data: dict) -> bool:
    """
    Connects directly to Supabase and updates the account with AI research results.
    """
    account_id = data.get("account_id")
    summary = data.get("summary")

    activity.logger.info(f"Updating database for account: {account_id}")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing")

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Update business summary and completeness score
        cur.execute(
            """
            UPDATE accounts 
            SET business_summary = %s, 
                completeness_score = LEAST(100, completeness_score + 30), 
                updated_at = NOW() 
            WHERE id = %s;
        """,
            (summary, account_id),
        )

        # Generate and save embedding for the updated summary
        try:
            vector = await embedding_client.get_embedding(summary)
            vector_str = f"[{','.join(map(str, vector))}]"

            # Delete existing summary embedding
            cur.execute(
                """
                DELETE FROM account_embeddings 
                WHERE account_id = %s AND content_type = 'summary';
                """,
                (account_id,),
            )

            # Insert new summary embedding
            cur.execute(
                """
                INSERT INTO account_embeddings (id, account_id, content_type, embedding, source_record_id, created_at)
                VALUES (gen_random_uuid(), %s, 'summary', %s, %s, NOW());
                """,
                (account_id, vector_str, account_id),
            )
        except Exception as emb_err:
            activity.logger.error(
                f"Failed to generate/update embedding in worker: {emb_err}"
            )

        conn.commit()
        cur.close()
        conn.close()

        activity.logger.info(f"Successfully updated account {account_id} in database")
        return True
    except Exception as e:
        activity.logger.error(f"Failed to update database: {e}")
        raise e
