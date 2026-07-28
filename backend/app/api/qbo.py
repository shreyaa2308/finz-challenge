from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from backend.app.db.mongodb import get_database
from backend.app.services.qbo_auth import (
    get_authorization_url,
    exchange_code_for_tokens,
    save_tokens,
    get_saved_tokens
)

router = APIRouter(prefix="/qbo", tags=["QuickBooks"])

@router.get("/connect")
async def connect():
    url = get_authorization_url()
    return RedirectResponse(url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")

    tokens = exchange_code_for_tokens(code, realm_id)

    db = get_database()
    await save_tokens(db, tokens)

    return {"status": "connected", "realm_id": realm_id}

import os
import requests

@router.get("/test-connection")
async def test_connection():
    db = get_database()
    tokens = await get_saved_tokens(db)

    realm_id = tokens["realm_id"]
    access_token = tokens["access_token"]

    environment = os.getenv("QBO_ENVIRONMENT", "sandbox")
    base_url = "https://sandbox-quickbooks.api.intuit.com" if environment == "sandbox" else "https://quickbooks.api.intuit.com"

    url = f"{base_url}/v3/company/{realm_id}/companyinfo/{realm_id}"

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
    )
    return response.json()

from backend.app.services.qbo_reports import get_qbo_pnl

@router.get("/pnl/{month}")
async def qbo_pnl(month: str):
    ranges = {
        "april": ("2026-04-01", "2026-04-30"),
        "may": ("2026-05-01", "2026-05-31"),
        "june": ("2026-06-01", "2026-06-30"),
        "quarter": ("2026-04-01", "2026-06-30")
    }
    start, end = ranges[month]
    db = get_database()
    return await get_qbo_pnl(db, start, end)