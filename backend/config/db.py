import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USER = os.environ.get("DB_USER", "job_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "job_password")
DB_NAME = os.environ.get("DB_NAME", "job_portal")

try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="job_portal_pool",
        pool_size=5,
        pool_reset_session=True,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    db_pool = None

def get_db_connection():
    if db_pool is None:
        raise Exception("Database connection pool is not initialized")
    return db_pool.get_connection()
