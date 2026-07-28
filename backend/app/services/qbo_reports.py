import os
import requests
from backend.app.services.qbo_auth import get_saved_tokens

def get_base_url():
    environment = os.getenv("QBO_ENVIRONMENT", "sandbox")
    return "https://sandbox-quickbooks.api.intuit.com" if environment == "sandbox" else "https://quickbooks.api.intuit.com"

async def get_qbo_pnl(db, start_date, end_date):
    tokens = await get_saved_tokens(db)
    realm_id = tokens["realm_id"]
    access_token = tokens["access_token"]
    base_url = get_base_url()

    url = f"{base_url}/v3/company/{realm_id}/reports/ProfitAndLoss"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "accounting_method": "Cash"
    }

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        },
        params=params
    )
    return response.json()