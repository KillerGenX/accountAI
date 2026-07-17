import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load env variables from root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

def test_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        sys.exit(1)

    print(f"Connecting to database at: {db_url.split('@')[-1]}...")
    
    try:
        # Connect to Postgres
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test 1: Get Postgres Version
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("SUCCESS: Connected to PostgreSQL!")
        print(f"   Database Version: {db_version[0]}")
        
        # Test 2: Check pgvector extension status
        cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        if vector_ext:
            print(f"SUCCESS: 'pgvector' extension is enabled! (Version: {vector_ext[1]})")
        else:
            print("WARNING: 'pgvector' extension is NOT enabled in your database yet.")
            print("   You can enable it by running: CREATE EXTENSION IF NOT EXISTS vector;")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
