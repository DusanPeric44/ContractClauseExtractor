import os
import argparse
import requests
from dotenv import load_dotenv


def run(pdf_path: str, api_base: str):
    with open(pdf_path, 'rb') as f:
        files = {'document': (os.path.basename(pdf_path), f, 'application/pdf')}
        r = requests.post(f"{api_base}/api/extract", files=files)
    r.raise_for_status()
    payload = r.json()
    print("Extract result:")
    print(payload)

    r = requests.get(f"{api_base}/api/extractions", params={"pageNum": 1, "pageSize": 10})
    r.raise_for_status()
    lst = r.json()
    print("Extractions list:")
    print(lst)
    if lst:
        doc_id = lst[0]["document_id"]
        r = requests.get(f"{api_base}/api/extractions/{doc_id}")
        r.raise_for_status()
        by_doc = r.json()
        print("Extractions by document:")
        print(by_doc)

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    
    demo_pdf = os.getenv("DEMO_PDF")
    if not demo_pdf:
        raise SystemExit("Missing DEMO_PDF. Set it in .env or provide --pdf.")

    api_base = os.getenv("API_BASE", "http://localhost:8001")
    if not api_base:
        raise SystemExit("Missing API_BASE. Set it in .env or provide --api.")
    
    parser.add_argument("--pdf", default=demo_pdf)
    parser.add_argument("--api", default=api_base)

    args = parser.parse_args()

    if not args.pdf:
        raise SystemExit("Missing --pdf. Provide a path or set DEMO_PDF.")
    run(args.pdf, args.api)