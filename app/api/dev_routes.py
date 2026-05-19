from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from typing import Optional, List

from app.services.backendbrain import (
    backend_brain
)

router = APIRouter()


# -----------------------------------
# DEV REQUEST MODEL
# -----------------------------------
class DevRequest(BaseModel):

    question: Optional[str] = None

    role: Optional[str] = None

    authentication_required: Optional[bool] = None

    allowed_roles: Optional[List[str]] = None

    allow_delete: Optional[bool] = None

    allow_update: Optional[bool] = None




# -----------------------------------
# DEV API
# -----------------------------------
@router.post("/dev/ask")
def dev_ask(request: DevRequest):

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
    return backend_brain(

        question=request.question,

        role = request.role,

        authentication_required=request.authentication_required,

        allowed_roles=request.allowed_roles,

        allow_delete=request.allow_delete,

        allow_update=request.allow_update,




    )