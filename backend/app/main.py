from fastapi import FastAPI
from backend.app.services.ingestion import read_excel_file
from backend.app.services.ingestion import read_bank_transactions

app = FastAPI(
    title="Finz Accounting Data Pipeline",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Finz Accounting Data Pipeline is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@app.get("/test-excel")
async def test_excel():
    return read_excel_file("backend/uploads/finz_dataset.xlsx")

@app.get("/test-transactions")
async def test_transactions():
    transactions = read_bank_transactions(
        "backend/uploads/finz_dataset.xlsx"
    )
    return {
        "count": len(transactions),
        "transactions": transactions[:5]
    }