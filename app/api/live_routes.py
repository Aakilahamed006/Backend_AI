from fastapi import APIRouter, HTTPException

from fastapi import Header

from pydantic import BaseModel

from typing import Optional, List

from app.services.backend_brain_live import (
    backendbrain_live
)

router = APIRouter()


# -----------------------------------
# LIVE REQUEST MODEL
# -----------------------------------
class LiveRequest(BaseModel):

    question: Optional[str] = None


    allow_delete: Optional[bool] = None

    allow_update: Optional[bool] = None


# -----------------------------------
# LIVE API
# -----------------------------------
@router.post("/live/ask")
def live_ask(

    request: LiveRequest,

    authorization: Optional[str] = Header(None)
):

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
    # EXTRACT JWT TOKEN
    # -----------------------------------
    token = None

    if authorization:

        token = authorization.replace(
            "Bearer ",
            ""
        )

    # -----------------------------------
    # BACKEND BRAIN
    # -----------------------------------
    return backendbrain_live(

        question=request.question,

        token=token,

        allow_delete=request.allow_delete,

        allow_update=request.allow_update,
    )