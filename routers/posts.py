from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Post as DBPost  # The Post model from models.py
from schemas import PostCreate, Post  # PostCreate and Post schemas for validation
from database import SessionLocal  # The session to connect to the database

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new post
@router.post("/posts/", response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = DBPost(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)  # Refresh the instance to get the generated ID
    return db_post

# Get a specific post by ID
@router.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# Get all posts
@router.get("/posts/", response_model=list[Post])
def get_posts(db: Session = Depends(get_db)):
    return db.query(DBPost).all()
