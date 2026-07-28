import os
import shutil
from fastapi import APIRouter, UploadFile, File
from backend.app.db.mongodb import get_database
from backend.app.services.ingestion import read_bank_transactions, ingest_transactions

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"]
)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    upload_path = f"backend/uploads/{file.filename}"

    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transactions = read_bank_transactions(upload_path)

    db = get_database()
    await ingest_transactions(db, transactions)

    return {
        "status": "success",
        "filename": file.filename,
        "processed_rows": len(transactions)
    }