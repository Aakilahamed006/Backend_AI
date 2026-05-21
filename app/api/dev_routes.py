from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List

from app.services.backendbrain import backend_brain

router = APIRouter()


# -----------------------------------
# REQUEST MODEL
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
def dev_ask(
    request: DevRequest,
    authorization: Optional[str] = Header(None)
):

    # -----------------------------------
    # VALIDATION
    # -----------------------------------
    if not request.question or request.question.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # -----------------------------------
    # EXTRACT JWT TOKEN
    # -----------------------------------
    token = None

    if request.authentication_required:
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        token = authorization.replace("Bearer ", "").strip()

    # -----------------------------------
    # BACKEND BRAIN CALL
    # -----------------------------------
    return backend_brain(
        question=request.question,
        token=token,
        role=request.role,
        authentication_required=request.authentication_required,
        allowed_roles=request.allowed_roles,
        allow_delete=request.allow_delete,
        allow_update=request.allow_update,
    )