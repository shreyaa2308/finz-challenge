from fastapi import FastAPI
from backend.app.services.ingestion import read_excel_file
from backend.app.services.ingestion import read_bank_transactions
from backend.app.db.mongodb import get_database
from backend.app.api.uploads import router as uploads_router
from backend.app.services.chart_of_accounts import read_chart_of_accounts, save_chart_of_accounts
from backend.app.api.transactions import router as transactions_router
from backend.app.api.pnl import router as pnl_router
from backend.app.api.qbo import router as qbo_router
from backend.app.api.sync import router as sync_router
from backend.app.api.reconciliation import router as reconciliation_router
from backend.app.api.classify import router as classify_router

app = FastAPI(
    title="Finz Accounting Data Pipeline",
    version="1.0.0"
)

app.include_router(uploads_router)
app.include_router(transactions_router)
app.include_router(pnl_router)
app.include_router(qbo_router)
app.include_router(sync_router)
app.include_router(reconciliation_router)
app.include_router(classify_router)


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


@app.get("/test-db")
async def test_database():
    db = get_database()

    await db.test.insert_one({
        "message": "MongoDB works"
    })

    result = await db.test.find_one(
        {"message": "MongoDB works"}
    )

    return {
        "database_connected": result is not None
    }


@app.post("/load-chart-of-accounts")
async def load_chart_of_accounts():
    accounts = read_chart_of_accounts("backend/uploads/finz_dataset.xlsx")
    db = get_database()
    await save_chart_of_accounts(db, accounts)
    return {"count": len(accounts)}