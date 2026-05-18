from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.backendbrain import (
    backend_brain
)

router = APIRouter()


# -----------------------------------
# PERMISSION MODEL
# -----------------------------------
class Permissions(BaseModel):

    allow_delete: bool = False

    allow_update: bool = False


# -----------------------------------
# REQUEST MODEL
# -----------------------------------
class QuestionRequest(BaseModel):

    question: Optional[str] = None

    permissions: Permissions = Permissions()


# -----------------------------------
# API ENDPOINT
# -----------------------------------
@router.post("/ask")
def home(request: QuestionRequest):

    # -----------------------------------
    # VALIDATION
    # -----------------------------------
    if (
        not request.question
        or request.question.strip() == ""
    ):

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # -----------------------------------
    # BACKEND BRAIN
    # -----------------------------------
    response = backend_brain(

        question=request.question,

        permissions=request.permissions.dict()
    )

    return {

        "success": True,

        "data": response
    }