from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.backendbrain import backend_brain


router = APIRouter()


class QuestionRequest(BaseModel):

    question: Optional[str] = None


@router.post("/ask")
def home(request: QuestionRequest):

    # -----------------------------
    # VALIDATION CHECK
    # -----------------------------
    if not request.question or request.question.strip() == "":

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    response = backend_brain(request.question)

    return {
        "success": True,
        "data": response
    }