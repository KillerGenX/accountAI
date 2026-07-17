import os
import json
import nats
import structlog

logger = structlog.get_logger()

class NATSClient:
    def __init__(self):
        self.nc = None
        self.js = None

    async def connect(self):
        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        try:
            self.nc = await nats.connect(nats_url)
            self.js = self.nc.jetstream()
            await logger.ainfo("nats_connected", url=nats_url)
        except Exception as e:
            await logger.aerror("nats_connection_failed", url=nats_url, error=str(e))
            raise e

    async def close(self):
        if self.nc:
            await self.nc.close()
            await logger.ainfo("nats_connection_closed")

    async def publish(self, subject: str, payload: dict):
        if not self.nc:
            raise RuntimeError("NATSClient is not connected. Call connect() first.")
        
        try:
            data = json.dumps(payload).encode("utf-8")
            # We publish using standard NATS publish
            await self.nc.publish(subject, data)
            await logger.ainfo("nats_event_published", subject=subject, payload=payload)
        except Exception as e:
            await logger.aerror("nats_publish_failed", subject=subject, error=str(e))
            raise e

# Create a global client instance
nats_client = NATSClient()
