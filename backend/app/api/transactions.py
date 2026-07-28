from fastapi import APIRouter
from bson import ObjectId
from backend.app.db.mongodb import get_database
from backend.app.services.corrections import save_correction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/")
async def list_transactions():
    db = get_database()
    cursor = db.transactions.find()
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    db = get_database()
    doc = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.patch("/{transaction_id}/classification")
async def update_classification(transaction_id: str, classification: dict):
    db = get_database()

    existing = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    old_classification = existing.get("classification", {}) if existing else {}
    old_account = old_classification.get("account_name")
    new_account = classification.get("account_name")

    if old_account and new_account and old_account != new_account:
        description = existing.get("description", "")
        pattern = description.upper()
        await save_correction(db, pattern, new_account)

    await db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"classification": classification}}
    )
    return {"updated": True}


@router.post("/{transaction_id}/approve")
async def approve_transaction(transaction_id: str):
    db = get_database()
    await db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"review_status": "approved"}}
    )
    return {"approved": True}

@router.post("/approve-all-classified")
async def approve_all_classified():
    db = get_database()
    result = await db.transactions.update_many(
        {"classification_status": "classified", "duplicate": False},
        {"$set": {"review_status": "approved"}}
    )
    return {"approved": result.modified_count}