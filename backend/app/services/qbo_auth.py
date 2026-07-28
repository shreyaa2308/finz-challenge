import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("QBO_CLIENT_ID")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("QBO_REDIRECT_URI")

AUTH_BASE_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

def get_authorization_url():
    scope = "com.intuit.quickbooks.accounting"
    return (
        f"{AUTH_BASE_URL}?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&state=random_state_string"
    )

def exchange_code_for_tokens(code, realm_id):
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Accept": "application/json"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )
    response.raise_for_status()
    tokens = response.json()
    tokens["realm_id"] = realm_id
    tokens["obtained_at"] = datetime.utcnow().isoformat()
    return tokens

async def save_tokens(db, tokens):
    await db.qbo_tokens.delete_many({})
    await db.qbo_tokens.insert_one(tokens)

async def get_saved_tokens(db):
    return await db.qbo_tokens.find_one()

def refresh_access_token(refresh_token):
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Accept": "application/json"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    response.raise_for_status()
    return response.json()