from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, Base, get_db

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic models for validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Add user to the database
    new_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.username = user.username
    existing_user.email = user.email
    existing_user.password = user.password
    db.commit()
    db.refresh(existing_user)
    return existing_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Add the new endpoints below the user-related routes

@app.get("/get-user-id/{username}")
def get_user_id_by_username(username: str, db: Session = Depends(get_db)):
    # Query the database to find the user by username
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id}


@app.get("/get-user-id")
def get_user_id(username: str, email: str, db: Session = Depends(get_db)):
    # Query the database with both username and email
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.email == email
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id}

# Serve the frontend HTML file
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    try:
        with open("index.html", "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found. Make sure the file exists in the same directory as main.py")
