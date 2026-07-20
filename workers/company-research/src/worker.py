# ruff: noqa: E402
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
from src.workflows import (
    CompanyResearchWorkflow,
    DailyAccountMonitoringWorkflow,
    ProspectingWorkflow,
)
from src.activities import (
    research_company_profile,
    update_account_in_db,
    detect_buying_signals,
    save_buying_signals_to_db,
    get_active_accounts_from_db,
    search_for_prospects,
    save_prospects_to_db,
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


async def handle_monitoring_event(msg):
    """
    NATS callback triggered when a manual 'account.monitoring_requested' event is published.
    Starts the asynchronous Temporal workflow to monitor all active accounts.
    """
    subject = msg.subject
    await logger.ainfo("nats_monitoring_event_received", subject=subject)

    try:
        # Start the Daily Account Monitoring Workflow in Temporal
        # We use a unique run ID prefix with timestamp or uuid to allow concurrent manual triggers if desired,
        # or a standard id to avoid concurrent duplicates of the harian scrape.
        # Let's use 'daily-monitoring-manual' as a single running instance to avoid concurrent duplicates of harian run.
        await temporal_client.start_workflow(
            DailyAccountMonitoringWorkflow.run,
            id="daily-monitoring-manual",
            task_queue="company-research-tasks",
        )
        await logger.ainfo("temporal_monitoring_workflow_started")
    except Exception as e:
        await logger.aerror(
            "failed_to_start_temporal_monitoring_workflow", error=str(e)
        )


async def handle_prospecting_event(msg):
    """
    NATS callback triggered when a 'prospecting.requested' event is published.
    """
    subject = msg.subject
    data = json.loads(msg.data.decode("utf-8"))
    await logger.ainfo("nats_prospecting_event_received", subject=subject, payload=data)

    workspace_id = data.get("workspace_id")
    if not workspace_id:
        return

    try:
        import uuid

        run_id = f"prospecting-{workspace_id}-{uuid.uuid4().hex[:6]}"
        await temporal_client.start_workflow(
            ProspectingWorkflow.run,
            data,
            id=run_id,
            task_queue="company-research-tasks",
        )
        await logger.ainfo("temporal_prospecting_workflow_started", run_id=run_id)
    except Exception as e:
        await logger.aerror("failed_to_start_prospecting_workflow", error=str(e))


async def main():
    global temporal_client

    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    temporal_url = os.getenv("TEMPORAL_URL", "localhost:7233")

    # 1. Connect to Temporal Server
    await logger.ainfo("connecting_to_temporal", url=temporal_url)
    temporal_client = await Client.connect(temporal_url)

    # 2. Connect to NATS and subscribe to events
    await logger.ainfo("connecting_to_nats", url=nats_url)
    nc = await nats.connect(nats_url)
    await nc.subscribe("account.created", cb=handle_nats_event)
    await nc.subscribe("account.monitoring_requested", cb=handle_monitoring_event)
    await nc.subscribe("prospecting.requested", cb=handle_prospecting_event)
    await logger.ainfo("nats_subscribed_to_subjects")

    # 3. Start Temporal Worker to process activities and workflows
    worker = Worker(
        temporal_client,
        task_queue="company-research-tasks",
        workflows=[
            CompanyResearchWorkflow,
            DailyAccountMonitoringWorkflow,
            ProspectingWorkflow,
        ],
        activities=[
            research_company_profile,
            update_account_in_db,
            detect_buying_signals,
            save_buying_signals_to_db,
            get_active_accounts_from_db,
            search_for_prospects,
            save_prospects_to_db,
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
