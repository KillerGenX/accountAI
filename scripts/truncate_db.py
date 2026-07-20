import os
import psycopg2
from dotenv import load_dotenv

# Load env variables from root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

def truncate_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        return
        
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Get all tables in public schema except alembic_version
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name != 'alembic_version'
            ORDER BY table_name;
        """)
        tables = [t[0] for t in cur.fetchall()]
        
        if not tables:
            print("No tables found in public schema.")
            return
            
        print(f"Found tables to truncate: {', '.join(tables)}")
        
        # Construct and run TRUNCATE query
        truncate_query = f"TRUNCATE TABLE {', '.join([f'\"{t}\"' for t in tables])} RESTART IDENTITY CASCADE;"
        print(f"Executing: {truncate_query}")
        cur.execute(truncate_query)
        conn.commit()
        
        print("Successfully truncated all public schema tables (with CASCADE).")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during database truncation: {e}")

if __name__ == "__main__":
    truncate_db()
