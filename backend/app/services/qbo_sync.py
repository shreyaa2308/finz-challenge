import os
import requests
from datetime import datetime
from backend.app.services.qbo_auth import get_saved_tokens

def get_base_url():
    environment = os.getenv("QBO_ENVIRONMENT", "sandbox")
    return "https://sandbox-quickbooks.api.intuit.com" if environment == "sandbox" else "https://quickbooks.api.intuit.com"

async def sync_transaction(db, transaction):
    if transaction.get("qbo_sync_status") == "synced":
        return {"skipped": True}

    tokens = await get_saved_tokens(db)
    realm_id = tokens["realm_id"]
    access_token = tokens["access_token"]
    base_url = get_base_url()

    classification = transaction.get("classification", {})
    account_name = classification.get("account_name")
    amount = abs(transaction.get("amount", 0))

    account_doc = await db.chart_of_accounts.find_one({"account_name": account_name})
    if not account_doc:
        await db.transactions.update_one(
            {"_id": transaction["_id"]},
            {"$set": {
                "qbo_sync_status": "failed",
                "error_message": f"Account '{account_name}' not found in chart of accounts",
                "attempt_count": transaction.get("attempt_count", 0) + 1
            }}
        )
        return {"error": "account_not_found"}

    is_income = transaction.get("amount", 0) > 0
    endpoint = "deposit" if is_income else "purchase"

    if is_income:
        payload = {
            "DepositToAccountRef": {"value": "35"},
            "Line": [{
                "Amount": amount,
                "DetailType": "DepositLineDetail",
                "DepositLineDetail": {
                    "AccountRef": {"value": account_doc.get("qbo_account_id", "1")}
                }
            }]
        }
    else:
        payload = {
            "PaymentType": "Cash",
            "AccountRef": {"value": "35"},
            "Line": [{
                "Amount": amount,
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {"value": account_doc.get("qbo_account_id", "1")}
                }
            }]
        }

    url = f"{base_url}/v3/company/{realm_id}/{endpoint}"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        qbo_id = result.get(endpoint.capitalize(), {}).get("Id")
        await db.transactions.update_one(
            {"_id": transaction["_id"]},
            {"$set": {
                "qbo_sync_status": "synced",
                "qbo_transaction_id": qbo_id,
                "synced_at": datetime.utcnow().isoformat()
            }}
        )
        return {"synced": True, "qbo_id": qbo_id}
    else:
        await db.transactions.update_one(
            {"_id": transaction["_id"]},
            {"$set": {
                "qbo_sync_status": "failed",
                "error_message": response.text,
                "attempt_count": transaction.get("attempt_count", 0) + 1
            }}
        )
        return {"error": response.text}


async def sync_all_approved(db):
    cursor = db.transactions.find({
        "review_status": "approved",
        "duplicate": False,
        "qbo_sync_status": {"$ne": "synced"}
    })
    results = []
    async for txn in cursor:
        result = await sync_transaction(db, txn)
        results.append(result)
    return results