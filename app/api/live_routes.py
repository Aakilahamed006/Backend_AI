from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from typing import Optional, List


from app.services.backend_brain_live import backendbrain_live

router = APIRouter()


# -----------------------------------
# LIVE REQUEST MODEL
# -----------------------------------
class LiveRequest(BaseModel):

    question: Optional[str] = None

    role: Optional[str] = None

    authentication_required: Optional[bool] = None

    allowed_roles: Optional[List[str]] = None

    allow_delete: Optional[bool] = None

    allow_update: Optional[bool] = None






# -----------------------------------
# LIVE API
# -----------------------------------
@router.post("/live/ask")
def live_ask(request: LiveRequest):

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
    return backendbrain_live(

        question=request.question,

        role=request.role,

        authentication_required=request.authentication_required,

        allow_delete=request.allow_delete,

        allow_update=request.allow_update,


    )