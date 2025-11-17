import os
import argparse
import requests


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
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--api", default="http://localhost:8001", help="API base URL")
    args = parser.parse_args()
    run(args.pdf, args.api)