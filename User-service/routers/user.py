from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.models import UserModel, TokenModel
from core.db import get_db
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

@router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered"}

@router.post("/login")
async def login_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "User logged in"}
