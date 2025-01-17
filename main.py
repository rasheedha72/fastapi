from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import bcrypt
from models import create_users_table
from database import get_db_connection
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Define a Token response model
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Hash password function
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Verify password function
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Generate JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Create User route (with password hashing)
@app.post("/users/")
def create_user(user: User):
    hashed_password = hash_password(user.password)
    query = """
    INSERT INTO users (name, email, password) 
    VALUES (%s, %s, %s) 
    RETURNING id, name, email;
    """
    with get_db_connection() as cursor:
        cursor.execute(query, (user.name, user.email, hashed_password))
        created_user = cursor.fetchone()
        return {"id": created_user[0], "name": created_user[1], "email": created_user[2]}

# Login route (password verification & token generation)
@app.post("/login/", response_model=TokenResponse)
def login(user: UserLogin):
    query = "SELECT id, name, email, password FROM users WHERE email = %s"
    with get_db_connection() as cursor:
        cursor.execute(query, (user.email,))
        db_user = cursor.fetchone()

    if db_user is None or not verify_password(user.password, db_user[3]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Create access token
    access_token = create_access_token(data={"sub": db_user[1]})  # Use the user's name as the subject
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route example
@app.get("/secure-data/")
def secure_data(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": f"Welcome, {user}! This is secure data."}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL!"}
