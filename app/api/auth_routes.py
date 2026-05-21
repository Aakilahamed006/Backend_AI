from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.database.connection import SessionLocal
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


# -----------------------------------
# SIGNUP MODEL
# -----------------------------------
class SignUpRequest(BaseModel):
    full_name: str
    email: str
    password: str


# -----------------------------------
# LOGIN MODEL
# -----------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


# -----------------------------------
# SIGNUP
# -----------------------------------
@router.post("/signup")
def signup(request: SignUpRequest):

    db = SessionLocal()

    try:
        # CHECK IF USER EXISTS
        existing_user = db.execute(
            text("""
                SELECT *
                FROM staff_users
                WHERE email = :email
            """),
            {"email": request.email}
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        # HASH PASSWORD
        hashed_password = hash_password(request.password)

        # INSERT USER
        db.execute(
            text("""
                INSERT INTO staff_users (
                    full_name,
                    email,
                    password_hash,
                    role,
                    is_active,
                    created_at
                )
                VALUES (
                    :full_name,
                    :email,
                    :password_hash,
                    :role,
                    :is_active,
                    NOW()
                )
            """),
            {
                "full_name": request.full_name,
                "email": request.email,
                "password_hash": hashed_password,
                "role": "user",
                "is_active": True
            }
        )

        db.commit()

        return {"message": "User created successfully"}

    finally:
        db.close()


# -----------------------------------
# LOGIN
# -----------------------------------
@router.post("/login")
def login(request: LoginRequest):

    db = SessionLocal()


    try:
        # FIND USER
        user = db.execute(
            text("""
                SELECT *
                FROM staff_users
                WHERE email = :email
            """),
            {"email": request.email}
        ).mappings().fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # CHECK IF ACTIVE
        if not user["is_active"]:
            raise HTTPException(
                status_code=403,
                detail="Account is disabled"
            )

        # VERIFY PASSWORD
        password_valid = verify_password(
            request.password,
            user["password_hash"]
        )

        if not password_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # CREATE JWT TOKEN
        token = create_access_token({
            "sub": user["email"],
            "role": user["role"]
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user["role"],
            "full_name": user["full_name"]
        }

    finally:
        db.close()