from fastapi import APIRouter

router = APIRouter()

@router.get("/{document_id}")
def get_extraction_by_id(document_id: int):
    return {"document_id": document_id}