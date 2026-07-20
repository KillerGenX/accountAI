import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load env variables from root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

def approve_request(email):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        return
        
    try:
        print(f"Connecting to database to approve request for: {email}")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Check if request exists and is pending
        cur.execute(
            "SELECT id, full_name, company_name, status FROM workspace_requests WHERE email = %s;",
            (email,)
        )
        row = cur.fetchone()
        
        if not row:
            print(f"Error: No access request found for email: {email}")
            cur.close()
            conn.close()
            return
            
        req_id, full_name, company_name, current_status = row
        print(f"Found request: ID={req_id}, Name={full_name}, Company={company_name}, Status={current_status}")
        
        if current_status == "approved":
            print("This request is already approved!")
            cur.close()
            conn.close()
            return
            
        # 2. Update status to approved
        print("Updating status to 'approved'...")
        cur.execute(
            "UPDATE workspace_requests SET status = 'approved', updated_at = now() WHERE email = %s;",
            (email,)
        )
        conn.commit()
        print("Request status updated to approved. PostgreSQL trigger fired successfully!")
        
        # 3. Query the newly created workspace and pending user to verify trigger action
        cur.execute(
            "SELECT id, name, company_name FROM workspaces WHERE name = %s;",
            (company_name,)
        )
        ws_row = cur.fetchone()
        if ws_row:
            print(f"✅ Created Workspace: ID={ws_row[0]}, Name={ws_row[1]}")
            
            # Check users table
            cur.execute(
                "SELECT id, email, role, status FROM users WHERE email = %s;",
                (email,)
            )
            usr_row = cur.fetchone()
            if usr_row:
                print(f"✅ Created Pending User: ID={usr_row[0]}, Email={usr_row[1]}, Role={usr_row[2]}, Status={usr_row[3]}")
                print("\nYou can now visit the register page:")
                print(f"http://localhost:3000/register?email={email}")
            else:
                print("❌ Trigger warning: Pending user was not created in 'users' table.")
        else:
            print("❌ Trigger warning: Workspace was not created in 'workspaces' table.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during request approval: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python approve_request.py <email>")
        sys.exit(1)
        
    email_to_approve = sys.argv[1].strip()
    approve_request(email_to_approve)
