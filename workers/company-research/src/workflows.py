from datetime import timedelta
from temporalio import workflow

# Import activities safely within Temporal workflow sandbox
with workflow.unsafe.imports_passed_through():
    from src.activities import research_company_profile, update_account_in_db


@workflow.defn
class CompanyResearchWorkflow:
    @workflow.run
    async def run(self, data: dict) -> str:
        company_name = data.get("company_name")
        account_id = data.get("account_id")

        # 1. Execute Company Research Activity
        summary = await workflow.execute_activity(
            research_company_profile,
            company_name,
            start_to_close_timeout=timedelta(seconds=60),
        )

        # 2. Execute DB Update Activity
        await workflow.execute_activity(
            update_account_in_db,
            {"account_id": account_id, "summary": summary},
            start_to_close_timeout=timedelta(seconds=60),
        )

        return summary
