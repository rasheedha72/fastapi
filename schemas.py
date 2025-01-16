from pydantic import BaseModel
from datetime import datetime

# Pydantic schema for creating a new user
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str

# Pydantic schema for returning user data (with hashed password)
class User(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Tells Pydantic to treat this as a model, not just a dict
