from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bcrypt
from models import create_users_table
from database import get_db_connection

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_users_table()
    print("Users table created successfully!")

# Define User models
class User(BaseModel):
    name: str
    email: str
    password: str  # Add password field

class UserLogin(BaseModel):
    email: str
    password: str

# Hash password function
def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Verify password function
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Create User route (with password hashing)
@app.post("/users/")
def create_user(user: User):
    hashed_password = hash_password(user.password)  # Hash the password
    query = """
    INSERT INTO users (name, email, password) 
    VALUES (%s, %s, %s) 
    RETURNING id, name, email;
    """
    with get_db_connection() as cursor:
        cursor.execute(query, (user.name, user.email, hashed_password))
        created_user = cursor.fetchone()
        return {"id": created_user[0], "name": created_user[1], "email": created_user[2]}

# Login route (password verification)
@app.post("/login/")
def login(user: UserLogin):
    query = "SELECT id, name, email, password FROM users WHERE email = %s"
    with get_db_connection() as cursor:
        cursor.execute(query, (user.email,))
        db_user = cursor.fetchone()

    if db_user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Verify the password
    if not verify_password(user.password, db_user[3]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {"message": "Login successful", "id": db_user[0], "name": db_user[1], "email": db_user[2]}

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL!"}
