from config.db import get_db_connection

def create_user(name, email, password_hash, role='seeker'):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, password_hash, role))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, name, email, role, created_at FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
