from typing import List
from fastapi import APIRouter
from models.extraction import Extraction
from models.metadata import Metadata

router = APIRouter()

@router.get("/{document_id}", response_model=Extraction)
def get_extraction_by_id(document_id: int):
    return Extraction(id=1, document_id=1, clauses=[], metadata=Metadata(id=1, extraction_id=1))

@router.get("", response_model=List[Extraction])
def get_extractions(pageNum: int, pageSize: int):
    return []