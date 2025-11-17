from typing import Annotated
import os
import json
import urllib.request
import asyncio

from fastapi import APIRouter, UploadFile, HTTPException

router = APIRouter()


@router.post("")
async def extract_clauses(document: UploadFile):
    data = await document.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    text = data.decode("utf-8", errors="ignore")
    result = await extract_clauses_from_document(text)
    return result


async def extract_clauses_from_document(text: str):
    return await asyncio.to_thread(_call_deepseek, text)


def _call_deepseek(text: str):
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    messages = [
        {"role": "system", "content": "You extract legal clauses and contract metadata. Return a strict JSON object with keys 'clauses' and 'metadata'. 'clauses' is an array of objects with 'name', 'text', 'start', 'end'. 'metadata' includes 'parties', 'effective_date', 'termination', 'governing_law', 'jurisdiction', 'payment_terms', 'renewal', 'confidentiality', 'liability_limit'."},
        {"role": "user", "content": text}
    ]
    payload = {
        "model": "deepseek-chat",
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "messages": messages
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8")
    except Exception:
        raise HTTPException(status_code=502, detail="LLM provider error")
    if status != 200:
        raise HTTPException(status_code=502, detail="LLM provider error")
    data = json.loads(body)
    content = data["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except Exception:
        return {"clauses": [], "metadata": {}}