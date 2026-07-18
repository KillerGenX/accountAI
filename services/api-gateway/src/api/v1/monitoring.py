from fastapi import APIRouter, Depends, HTTPException, status
import structlog
from src.core.nats_client import nats_client
from src.core.auth import require_role

logger = structlog.get_logger()
router = APIRouter(tags=["Monitoring"])


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_daily_monitoring(
    current_user: dict = Depends(require_role(["administrator", "account_manager"])),
):
    """
    Manually triggers the Daily Scraper/Monitoring Workflow for all active accounts.
    """
    await logger.ainfo(
        "manual_daily_monitoring_triggered",
        user_id=current_user["id"],
        workspace_id=current_user["workspace_id"],
    )

    try:
        # Publish trigger event to NATS event bus
        event_payload = {
            "triggered_by": current_user["id"],
            "workspace_id": current_user["workspace_id"],
        }
        await nats_client.publish("account.monitoring_requested", event_payload)
    except Exception as e:
        await logger.aerror(
            "nats_publish_monitoring_requested_failed",
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue the monitoring workflow.",
        )

    return {"status": "success", "message": "Daily monitoring workflow triggered."}
