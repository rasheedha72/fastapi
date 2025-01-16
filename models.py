from passlib.context import CryptContext
from database import get_db_connection

# Create a password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create users table with password field
def create_users_table():
    drop_table_query = "DROP TABLE IF EXISTS users;"
    create_table_query = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """
    with get_db_connection() as cursor:
        cursor.execute(drop_table_query)  # Drop the table if it exists
        cursor.execute(create_table_query)  # Create the table
