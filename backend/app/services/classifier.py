import os
import json
from google import genai
from dotenv import load_dotenv
from backend.app.config.transaction_types import ALLOWED_TYPES

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


async def classify_with_gemini(transaction, chart_of_accounts):
    account_list = "\n".join(
        f"{a['account_number']} - {a['account_name']} ({a['account_type']})"
        for a in chart_of_accounts
    )
    prompt = f"""
Transaction:
Description: {transaction.get('description')}
Amount: {transaction.get('amount')}
Bank Account: {transaction.get('bank_account')}

Allowed transaction types: {", ".join(ALLOWED_TYPES)}

Allowed QBO accounts:
{account_list}

Return ONLY valid JSON with these fields:
transaction_type, counterparty, account_name, confidence (0-1), explanation
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return json.loads(response.text)


def validate_classification(classification, chart_of_accounts):
    allowed_account_names = {a["account_name"] for a in chart_of_accounts}

    if classification.get("transaction_type") not in ALLOWED_TYPES:
        return "needs_review"
    if classification.get("account_name") not in allowed_account_names:
        return "needs_review"
    confidence = classification.get("confidence")
    if confidence is None or not (0 <= confidence <= 1):
        return "needs_review"
    return "pending"