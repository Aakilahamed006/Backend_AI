from fastapi import APIRouter

from app.services.ai_service import ask_ai
from app.services.backendbrain import backend_brain


router = APIRouter()

@router.get("/")
def home():
    question = (
       "add user where name is nafil and age is 35"

    )

    response = backend_brain(question)

    return response