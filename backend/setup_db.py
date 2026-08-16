import os
import mysql.connector
from dotenv import load_dotenv
import bcrypt

load_dotenv()

def initialize_database():
    print("Connecting to MySQL...")
    try:
        # Connect without database first to create it
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "127.0.0.1"),
            port=os.environ.get("DB_PORT", "3306"),
            user=os.environ.get("DB_USER", "job_user"),
            password=os.environ.get("DB_PASSWORD", "job_password")
        )
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        print("Executing schema.sql...")
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Execute statements individually
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        for command in sql_commands:
            cursor.execute(command)
            
        print("Database schema created successfully.")
        
        # Seed Data
        cursor.execute("USE job_portal;")
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            print("Inserting seed data...")
            hashed_pw = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert Employer
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role) 
                VALUES ('Acme Corp', 'employer@acme.com', %s, 'employer')
            """, (hashed_pw,))
            employer_id = cursor.lastrowid
            
            # Insert Job Seeker
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role) 
                VALUES ('John Doe', 'john@example.com', %s, 'seeker')
            """, (hashed_pw,))
            seeker_id = cursor.lastrowid
            
            # Insert Job
            cursor.execute("""
                INSERT INTO jobs (employer_id, title, company, description, requirements, salary, location, type) 
                VALUES (%s, 'Software Engineer', 'Acme Corp', 'Develop awesome stuff', 'Python, MySQL', '$100k - $120k', 'Remote', 'Full-time')
            """, (employer_id,))
            job_id = cursor.lastrowid
            
            # Insert Application
            cursor.execute("""
                INSERT INTO applications (job_id, user_id, resume_link, status) 
                VALUES (%s, %s, 'http://example.com/resume.pdf', 'pending')
            """, (job_id, seeker_id))
            
            conn.commit()
            print("Seed data inserted successfully.")
            print(f"Employer: employer@acme.com / password123")
            print(f"Seeker: john@example.com / password123")
        else:
            print("Database already contains data. Skipping seed.")
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    initialize_database()
