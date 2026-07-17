import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

def check_data():
    db_url = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Query Workspaces
        cur.execute("SELECT id, name, company_name FROM workspaces;")
        workspaces = cur.fetchall()
        print("Workspaces in DB:")
        for w in workspaces:
            print(f" - ID: {w[0]}, Name: {w[1]}, Company: {w[2]}")
            
        # 2. Query Users
        cur.execute("SELECT id, workspace_id, email, full_name, role, status FROM users;")
        users = cur.fetchall()
        print("\nUsers in DB:")
        for u in users:
            print(f" - ID: {u[0]}, Workspace ID: {u[1]}, Email: {u[2]}, Name: {u[3]}, Role: {u[4]}, Status: {u[5]}")

        # 3. Query Accounts
        cur.execute("SELECT id, workspace_id, company_name, completeness_score FROM accounts;")
        accounts = cur.fetchall()
        print("\nAccounts in DB:")
        for a in accounts:
            print(f" - ID: {a[0]}, Workspace ID: {a[1]}, Name: {a[2]}, Completeness: {a[3]}")

        # 4. Query Contacts
        cur.execute("SELECT id, account_id, full_name, title, is_primary FROM contacts;")
        contacts = cur.fetchall()
        print("\nContacts in DB:")
        for co in contacts:
            print(f" - ID: {co[0]}, Account ID: {co[1]}, Name: {co[2]}, Title: {co[3]}, Primary: {co[4]}")

        # 5. Query Notes
        cur.execute("SELECT id, account_id, user_id, content FROM account_notes;")
        notes = cur.fetchall()
        print("\nAccount Notes in DB:")
        for n in notes:
            print(f" - ID: {n[0]}, Account ID: {n[1]}, Author User ID: {n[2]}, Content: {n[3][:60]}...")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    check_data()
