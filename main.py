from fastapi import FastAPI

from routers import extract, extractions

app = FastAPI(title="Contract Clause Extractor",
              version="1.0",
              description="API for extracting clauses from contract documents")

app.include_router(extract.router, prefix="/extract", tags=["extract"])
app.include_router(extractions.router, prefix="/extractions", tags=["extractions"])


