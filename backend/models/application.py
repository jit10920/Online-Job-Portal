from config.db import get_db_connection

def create_application(job_id, user_id, resume_link=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "INSERT INTO applications (job_id, user_id, resume_link) VALUES (%s, %s, %s)"
        cursor.execute(query, (job_id, user_id, resume_link))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_applications_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT a.*, j.title, j.company, j.location 
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.user_id = %s
            ORDER BY a.applied_at DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_applications_by_job(job_id, employer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify job belongs to employer
        query = """
            SELECT a.*, u.name, u.email 
            FROM applications a
            JOIN users u ON a.user_id = u.id
            JOIN jobs j ON a.job_id = j.id
            WHERE a.job_id = %s AND j.employer_id = %s
            ORDER BY a.applied_at DESC
        """
        cursor.execute(query, (job_id, employer_id))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_application_status(application_id, employer_id, status):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Ensure the employer owns the job this application is for
        query = """
            UPDATE applications a
            JOIN jobs j ON a.job_id = j.id
            SET a.status = %s
            WHERE a.id = %s AND j.employer_id = %s
        """
        cursor.execute(query, (status, application_id, employer_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
