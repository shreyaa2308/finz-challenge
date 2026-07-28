async def find_duplicate(db, transaction):
    transaction_id = transaction.get("source_transaction_id")
    bank_account = transaction.get("bank_account")
    if transaction_id:
        existing = await db.transactions.find_one({
            "source_transaction_id": transaction_id,
            "bank_account": bank_account,
            "duplicate": False
        })
        return existing
    return None