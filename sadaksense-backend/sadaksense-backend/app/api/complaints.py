from fastapi import APIRouter, HTTPException
from app.schemas import ComplaintRequest, ComplaintResponse
from app.services import complaint

router = APIRouter(prefix="/v1", tags=["complaints"])


@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(req: ComplaintRequest):
    try:
        return await complaint.draft(req)
    except ValueError as e:
        raise HTTPException(422, str(e))
