import asyncio
import os
import sys
import json
import nats
import structlog
from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv

# Add workers parent folder to sys.path so src imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env variables from root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Import workflows and activities
from src.workflows import CompanyResearchWorkflow  # noqa: E402
from src.activities import (  # noqa: E402
    research_company_profile,
    update_account_in_db,
    detect_buying_signals,
    save_buying_signals_to_db,
)  # noqa: E402

# Global Temporal client
temporal_client = None


async def handle_nats_event(msg):
    """
    NATS callback triggered when a new 'account.created' event is published.
    Starts the asynchronous Temporal workflow to research the company.
    """
    subject = msg.subject
    data = json.loads(msg.data.decode("utf-8"))

    await logger.ainfo("nats_event_received", subject=subject, payload=data)

    account_id = data.get("id")
    company_name = data.get("company_name")

    if not account_id or not company_name:
        await logger.awarn("invalid_event_payload_missing_fields")
        return

    try:
        # Start the Company Research Workflow in Temporal
        await temporal_client.start_workflow(
            CompanyResearchWorkflow.run,
            {"account_id": account_id, "company_name": company_name},
            id=f"research-{account_id}",
            task_queue="company-research-tasks",
        )
        await logger.ainfo("temporal_workflow_started", account_id=account_id)
    except Exception as e:
        await logger.aerror(
            "failed_to_start_temporal_workflow", account_id=account_id, error=str(e)
        )


async def main():
    global temporal_client

    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    temporal_url = os.getenv("TEMPORAL_URL", "localhost:7233")

    # 1. Connect to Temporal Server
    await logger.ainfo("connecting_to_temporal", url=temporal_url)
    temporal_client = await Client.connect(temporal_url)

    # 2. Connect to NATS and subscribe to account.created
    await logger.ainfo("connecting_to_nats", url=nats_url)
    nc = await nats.connect(nats_url)
    await nc.subscribe("account.created", cb=handle_nats_event)
    await logger.ainfo("nats_subscribed_to_subject", subject="account.created")

    # 3. Start Temporal Worker to process activities and workflows
    worker = Worker(
        temporal_client,
        task_queue="company-research-tasks",
        workflows=[CompanyResearchWorkflow],
        activities=[
            research_company_profile,
            update_account_in_db,
            detect_buying_signals,
            save_buying_signals_to_db,
        ],
    )

    await logger.ainfo("temporal_worker_running", task_queue="company-research-tasks")

    try:
        # Block and run the worker loop (keeps NATS callback listening)
        await worker.run()
    except asyncio.CancelledError:
        pass
    finally:
        await nc.close()
        await logger.ainfo("connections_closed_worker_terminated")


if __name__ == "__main__":
    asyncio.run(main())
