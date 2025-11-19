import os
import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    os.environ["DB_PATH"] = str(db_file)

    from main import app

    async def fake_extract_clauses_from_document(text: str):
        payload = {
            "clauses": [
                {"name": "Termination", "text": "Short text", "start": 0, "end": 10},
                {"name": "Payment", "text": "Short text", "start": 11, "end": 20},
            ],
            "metadata": {
                "parties": ["A", "B"],
                "effective_date": "2024-01-01",
                "termination": "30 days notice",
                "governing_law": "NY",
                "jurisdiction": "NYC",
                "payment_terms": "Net 30",
                "renewal": "Auto",
                "confidentiality": "Standard",
                "liability_limit": "Cap"
            }
        }
        return json.dumps(payload)

    # Avoid real PDF/DOCX parsing by forcing a fixed text
    async def fake_extract_text(file):
        return "contract text"

    import routers.extract as extract_router
    import services.text_extraction_service as text_service
    monkeypatch.setattr(extract_router, "extract_clauses_from_document", fake_extract_clauses_from_document)
    monkeypatch.setattr(text_service, "extract_text", fake_extract_text)

    with TestClient(app) as c:
        yield c


def test_extract_pdf_success(client):
    files = {"document": ("sample.pdf", b"%PDF-1.4\n...", "application/pdf")}
    r = client.post("/api/extract", files=files)
    assert r.status_code == 200
    payload = r.json()
    assert "clauses" in payload and "metadata" in payload
    assert len(payload["clauses"]) == 2

    r = client.get("/api/extractions", params={"pageNum": 1, "pageSize": 10})
    assert r.status_code == 200
    lst = r.json()
    assert isinstance(lst, list)
    assert len(lst) >= 1

    doc_id = lst[0]["document_id"]
    r = client.get(f"/api/extractions/{doc_id}")
    assert r.status_code == 200
    by_doc = r.json()
    assert isinstance(by_doc, list)
    assert by_doc and by_doc[0]["document_id"] == doc_id


def test_extract_docx_success(client):
    files = {"document": ("sample.docx", b"PK\x03\x04...", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    r = client.post("/api/extract", files=files)
    assert r.status_code == 200
    payload = r.json()
    assert "clauses" in payload and "metadata" in payload


def test_extract_unsupported_type(client):
    files = {"document": ("sample.txt", b"hello", "text/plain")}
    r = client.post("/api/extract", files=files)
    assert r.status_code == 400
    assert r.json()["detail"] == "Unsupported file type"