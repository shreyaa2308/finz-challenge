from fastapi import APIRouter
from backend.app.db.mongodb import get_database
from backend.app.services.rule_classifier import rule_based_classify
from backend.app.services.classifier import classify_with_gemini, validate_classification

router = APIRouter(prefix="/classify", tags=["Classification"])

@router.post("/run")
async def run_classification():
    db = get_database()
    accounts = [a async for a in db.chart_of_accounts.find()]

    cursor = db.transactions.find({
        "duplicate": False,
        "classification_status": "pending"
    })

    processed = 0
    async for txn in cursor:
        description = txn.get("description") or ""

        rule_result = rule_based_classify(description)
        if rule_result:
            classification = {
                "transaction_type": rule_result.get("transaction_type"),
                "counterparty": None,
                "account_name": rule_result.get("account_name", "Uncategorized"),
                "confidence": 1.0,
                "explanation": "Matched deterministic rule"
            }
            status = "pending"
        else:
            try:
                classification = await classify_with_gemini(txn, accounts)
                status = validate_classification(classification, accounts)
            except Exception as e:
                classification = {
                    "transaction_type": "operating_expense",
                    "account_name": "Uncategorized",
                    "confidence": 0,
                    "explanation": f"Gemini error: {str(e)}"
                }
                status = "needs_review"

        await db.transactions.update_one(
            {"_id": txn["_id"]},
            {"$set": {
                "classification": classification,
                "classification_status": "classified",
                "review_status": status
            }}
        )
        processed += 1

    return {"classified": processed}