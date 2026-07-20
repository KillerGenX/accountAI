import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

async def test_conn(host, port):
    db_user = "postgres.szobxzekrawxsmpsyzrj"
    db_pass = "@1996Passmein"
    db_name = "postgres"
    
    print(f"\nTesting connection to {host}:{port}...")
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(
                user=db_user,
                password=db_pass,
                database=db_name,
                host=host,
                port=port,
                timeout=5
            ),
            timeout=6
        )
        print(f"SUCCESS: Successfully connected to {host}:{port}!")
        version = await conn.fetchval("SELECT version();")
        print(f"PostgreSQL version: {version}")
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR connecting to {host}:{port} - Exception: {e}")
        return False

async def main():
    await test_conn("aws-0-ap-southeast-1.pooler.supabase.com", 6543)

if __name__ == "__main__":
    asyncio.run(main())
