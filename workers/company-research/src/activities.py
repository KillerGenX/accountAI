import os
import psycopg2
from temporalio import activity
from dotenv import load_dotenv

# Load env variables from root folder (.env is 2 levels up from workers/company-research/src/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


@activity.defn
async def research_company_profile(company_name: str) -> str:
    """
    Simulates AI research of a corporate profile.
    In a real app, this would query OpenAI/Perplexity search APIs.
    """
    activity.logger.info(f"Researching company profile for: {company_name}")

    # Mock AI research summary response
    mock_summary = (
        f"{company_name} is a leading enterprise player. In recent years, they have been "
        f"focused on expanding their digital capabilities, migrating IT workloads to multi-cloud platforms, "
        f"and investing in AI-driven operational efficiency. Key initiatives include modernization "
        f"of legacy architecture and strategic partnerships with global tech vendors. Their current "
        f"technology stack focuses on modern web frameworks and enterprise cloud services."
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

        conn.commit()
        cur.close()
        conn.close()

        activity.logger.info(f"Successfully updated account {account_id} in database")
        return True
    except Exception as e:
        activity.logger.error(f"Failed to update database: {e}")
        raise e
