import psycopg2
from psycopg2 import sql
from contextlib import contextmanager

# Database connection details (update with your details)
DATABASE_URL = "postgresql://postgres:rashee%402005@localhost:5432/fastapi"

# Context manager for database connections
@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()  # Commit changes after execution
    finally:
        cursor.close()
        conn.close()
