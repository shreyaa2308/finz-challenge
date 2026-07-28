import pandas as pd

def read_chart_of_accounts(file_path: str):
    df = pd.read_excel(file_path, sheet_name="QBO Chart of Accounts", header=3)
    df = df.dropna(how="all")
    df = df.where(pd.notnull(df), None)
    raw_records = df.to_dict(orient="records")

    accounts = []
    for r in raw_records:
        accounts.append({
            "account_number": str(r.get("Account No.")),
            "account_name": r.get("Account Name"),
            "account_type": r.get("QBO Account Type"),
            "detail_type": r.get("Suggested Detail Type"),
            "statement": r.get("Statement"),
            "purpose": r.get("Purpose"),
            "active": r.get("Active")
        })
    return accounts


async def save_chart_of_accounts(db, accounts):
    await db.chart_of_accounts.delete_many({})
    await db.chart_of_accounts.insert_many(accounts)