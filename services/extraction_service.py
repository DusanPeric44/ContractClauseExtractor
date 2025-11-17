from typing import List
from models.document import DocumentBase
from models.clause import Clause, ClauseBase
from models.metadata import Metadata, MetadataBase
from models.extraction import Extraction
from repositories import document_repository, extraction_repository, clause_repository, metadata_repository


async def save_extraction(filename: str, text: str, payload: dict) -> dict:
    doc_id = await document_repository.insert(DocumentBase(name=filename, text=text))
    extraction_id = await extraction_repository.insert(doc_id)

    clauses_data = payload.get('clauses', [])
    clauses = [ClauseBase(**c, extraction_id=extraction_id) for c in clauses_data]
    await clause_repository.insert_many(clauses)

    metadata_data = payload.get('metadata', {})
    metadata = MetadataBase(**metadata_data, extraction_id=extraction_id)
    await metadata_repository.insert(metadata)

    return payload


async def get_by_document_id(document_id: int) -> List[Extraction]:
    rows = await extraction_repository.get_by_document_id(document_id)
    result: List[Extraction] = []
    for r in rows:
        eid = r[0]
        clause_rows = await clause_repository.get_by_extraction_id(eid)
        metadata_row = await metadata_repository.get_by_extraction_id(eid)
        result.append(
            Extraction(
                id=eid,
                document_id=document_id,
                clauses=[Clause(**cr) for cr in clause_rows],
                metadata=Metadata(**metadata_row) if metadata_row else Metadata(id=0, extraction_id=eid),
            )
        )
    return result


async def list_extractions(pageNum: int, pageSize: int) -> List[Extraction]:
    rows = await extraction_repository.list(pageNum, pageSize)
    result: List[Extraction] = []
    for r in rows:
        eid = r[0]
        doc_id = r[1]
        clause_rows = await clause_repository.get_by_extraction_id(eid)
        metadata_row = await metadata_repository.get_by_extraction_id(eid)
        result.append(
            Extraction(
                id=eid,
                document_id=doc_id,
                clauses=[Clause(**cr) for cr in clause_rows],
                metadata=Metadata(**metadata_row) if metadata_row else Metadata(id=0, extraction_id=eid),
            )
        )
    return result