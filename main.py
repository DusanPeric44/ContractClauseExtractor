import uvicorn
from fastapi import FastAPI

from routers import extract, extractions

app = FastAPI(title="Contract Clause Extractor",
              version="1.0",
              description="API for extracting clauses from contract documents")

app.include_router(extract.router, prefix="/api/extract", tags=["extract"])
app.include_router(extractions.router, prefix="/api/extractions", tags=["extractions"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
