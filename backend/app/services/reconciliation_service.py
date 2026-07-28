from backend.app.services.pnl_service import generate_pnl
from backend.app.services.qbo_reports import get_qbo_pnl

def parse_qbo_pnl_rows(qbo_report):
    accounts = {}
    rows = qbo_report.get("Rows", {}).get("Row", [])

    def walk(row_list):
        for row in row_list:
            if "ColData" in row:
                col_data = row["ColData"]
                if len(col_data) >= 2:
                    name = col_data[0].get("value")
                    try:
                        amount = float(col_data[1].get("value", 0))
                    except (ValueError, TypeError):
                        amount = 0
                    accounts[name] = amount
            if "Rows" in row:
                walk(row["Rows"].get("Row", []))

    walk(rows)
    return accounts

async def reconcile(db, start_date, end_date):
    app_pnl = await generate_pnl(db, start_date, end_date)
    qbo_report = await get_qbo_pnl(db, start_date, end_date)
    qbo_accounts = parse_qbo_pnl_rows(qbo_report)

    comparison = {
        "Net Profit": {
            "application_amount": app_pnl["net_profit"],
            "quickbooks_amount": qbo_accounts.get("Net Income", 0),
        }
    }

    results = []
    for account, values in comparison.items():
        diff = round(values["application_amount"] - values["quickbooks_amount"], 2)
        results.append({
            "account": account,
            "application_amount": values["application_amount"],
            "quickbooks_amount": values["quickbooks_amount"],
            "difference": diff,
            "status": "reconciled" if abs(diff) < 0.01 else "mismatch",
            "explanation": None if abs(diff) < 0.01 else "Amounts differ, review classification mapping"
        })
    return results