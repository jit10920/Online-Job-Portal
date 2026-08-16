from config.db import get_db_connection

def create_job(employer_id, title, company, description, requirements, salary, location, job_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            INSERT INTO jobs (employer_id, title, company, description, requirements, salary, location, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (employer_id, title, company, description, requirements, salary, location, job_type))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_all_jobs(filters=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM jobs WHERE status = 'open'"
        params = []
        
        if filters:
            if filters.get('location'):
                query += " AND location LIKE %s"
                params.append(f"%{filters['location']}%")
            if filters.get('type'):
                query += " AND type = %s"
                params.append(filters['type'])
            if filters.get('keyword'):
                query += " AND (title LIKE %s OR description LIKE %s OR company LIKE %s)"
                params.extend([f"%{filters['keyword']}%", f"%{filters['keyword']}%", f"%{filters['keyword']}%"])
                
        query += " ORDER BY created_at DESC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_job_by_id(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM jobs WHERE id = %s"
        cursor.execute(query, (job_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_job(job_id, employer_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Ensure only the employer who created it can update it
        allowed_fields = ['title', 'company', 'description', 'requirements', 'salary', 'location', 'type', 'status']
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = %s")
                params.append(value)
        
        if not updates:
            return False
            
        query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = %s AND employer_id = %s"
        params.extend([job_id, employer_id])
        
        cursor.execute(query, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def delete_job(job_id, employer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "DELETE FROM jobs WHERE id = %s AND employer_id = %s"
        cursor.execute(query, (job_id, employer_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
