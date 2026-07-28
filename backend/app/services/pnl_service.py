from datetime import datetime

EXCLUDED_TYPES = {"transfer", "owner_activity", "fixed_asset_purchase"}

async def generate_pnl(db, start_date, end_date):
    cursor = db.transactions.find({
        "duplicate": False,
        "transaction_date": {"$gte": start_date, "$lte": end_date}
    })

    revenue = refunds = cogs = opex = 0

    async for txn in cursor:
        classification = txn.get("classification", {})
        t_type = classification.get("transaction_type")
        amount = txn.get("amount", 0)

        if t_type in EXCLUDED_TYPES:
            continue
        if t_type == "revenue":
            revenue += amount
        elif t_type == "refund":
            refunds += amount
        elif t_type == "cogs":
            cogs += amount
        elif t_type == "operating_expense":
            opex += amount

    net_revenue = revenue - refunds
    gross_profit = net_revenue - cogs
    net_profit = gross_profit - opex

    return {
        "revenue": revenue,
        "refunds": refunds,
        "net_revenue": net_revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "operating_expenses": opex,
        "net_profit": net_profit
    }