import asyncio
import os
import sys
from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
)
from dotenv import load_dotenv

# Add workers parent folder to sys.path so src imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env variables from root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

from src.workflows import DailyAccountMonitoringWorkflow  # noqa: E402


async def main():
    temporal_url = os.getenv("TEMPORAL_URL", "localhost:7233")
    print(f"Connecting to Temporal at {temporal_url}...")
    client = await Client.connect(temporal_url)

    schedule_id = "daily-account-monitoring-schedule"

    try:
        print(f"Registering schedule '{schedule_id}' (running harian jam 06:00 AM)...")
        await client.create_schedule(
            schedule_id,
            Schedule(
                action=ScheduleActionStartWorkflow(
                    DailyAccountMonitoringWorkflow.run,
                    id="daily-account-monitoring-cron",
                    task_queue="company-research-tasks",
                ),
                spec=ScheduleSpec(
                    # Run daily at 06:00 AM UTC
                    cron_expressions=["0 6 * * *"]
                ),
            ),
        )
        print("Schedule registered successfully!")
    except Exception as e:
        if "already exists" in str(e).lower() or "ScheduleAlreadyRunning" in str(e):
            print("Schedule already exists, updating existing schedule...")
            schedule_handle = client.get_schedule_handle(schedule_id)
            await schedule_handle.update(
                lambda update_input: Schedule(
                    action=ScheduleActionStartWorkflow(
                        DailyAccountMonitoringWorkflow.run,
                        id="daily-account-monitoring-cron",
                        task_queue="company-research-tasks",
                    ),
                    spec=ScheduleSpec(cron_expressions=["0 6 * * *"]),
                )
            )
            print("Schedule updated successfully!")
        else:
            print(f"Failed to register schedule: {e}")


if __name__ == "__main__":
    asyncio.run(main())
