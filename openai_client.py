import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException

def call_deepseek(text: str):
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    system_prompt = """
       You extract legal clauses and contract metadata from a text you are prompted with.
       Return a strict JSON object with keys 'clauses' and 'metadata'.
       'clauses' is an array of objects with 'name', 'text', 'start', 'end'.
       Limit each clause 'text' to at most 400 characters.
       'metadata' includes 'parties', 'effective_date', 'termination', 'governing_law',
       'jurisdiction', 'payment_terms', 'renewal', 'confidentiality', 'liability_limit'.
       Output only valid JSON. No prose and no code fences.
    """

    user_prompt = text

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=8000,
            response_format={
                'type': 'json_object'
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {e}")