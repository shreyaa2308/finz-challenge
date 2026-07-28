import io
import pandas as pd
from backend.app.services.normalization import normalize_transaction
from backend.app.services.duplicate_detector import find_duplicate

def read_excel_file(file_path: str):
    workbook = pd.ExcelFile(file_path)
    return {
        "sheet_names": workbook.sheet_names
    }


def read_bank_transactions(file_source):
    """Reads transactions from either a file path or file bytes (io.BytesIO)."""
    df = pd.read_excel(
        file_source,
        sheet_name="Raw Bank Transactions",
        header=3
    )
    df = df.dropna(how="all")
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


async def ingest_transactions(db, transactions):
    # Clear old test data
    await db.raw_transactions.delete_many({})
    await db.transactions.delete_many({})

    inserted_count = 0

    for raw in transactions:
        # Skip empty rows where all fields are None
        if not raw or all(v is None for v in raw.values()):
            continue

        try:
            raw_result = await db.raw_transactions.insert_one({
                "raw_record": raw
            })
            
            normalized = normalize_transaction(raw)
            normalized["raw_record_id"] = str(raw_result.inserted_id)
            existing = await find_duplicate(db, normalized)
            if existing:
                normalized["duplicate"] = True
                normalized["duplicate_of"] = str(existing["_id"])
            
            await db.transactions.insert_one(normalized)
            inserted_count += 1
            
        except ValueError:
            # Skip any corrupt or incomplete blank row gracefully
            continue

    return inserted_count