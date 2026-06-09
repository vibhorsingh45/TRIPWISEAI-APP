from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, LoginIn, TokenOut, UserOut
from app.utils.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(name=body.name, email=body.email, password_hash=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token(user.id, user.email)
    return {"access_token": token, "user": UserOut.model_validate(user)}

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(user.id, user.email)
    return {"access_token": token, "user": UserOut.model_validate(user)}
