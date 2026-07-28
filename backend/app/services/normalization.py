from datetime import datetime


def normalize_text(value):
    if value is None:
        return None

    return " ".join(
        str(value).strip().split()
    )


def normalize_currency(value):
    if not value:
        return "USD"

    return str(value).strip().upper()


def normalize_amount(value):
    if value is None:
        raise ValueError("Amount is missing")

    if isinstance(value, str):
        value = (
            value
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

    return float(value)


def normalize_date(value):
    if value is None:
        raise ValueError("Date is missing")

    if isinstance(value, datetime):
        return value.date().isoformat()

    return str(value)

def normalize_transaction(raw):
    return {
        "source_transaction_id":
            raw.get("Bank Transaction ID"),

        "transaction_date":
            normalize_date(
                raw.get("Transaction Date")
            ),

        "posted_date":
            normalize_date(
                raw.get("Posted Date")
            ),

        "description":
            normalize_text(
                raw.get("Description")
            ),

        "amount":
            normalize_amount(
                raw.get("Amount (USD)")
            ),

        "currency":
            normalize_currency(
                raw.get("Currency")
            ),

        "bank_account":
            normalize_text(
                raw.get("Bank Account")
            ),

        "duplicate": False,

        "classification_status":
            "pending",

        "review_status":
            "pending",

        "qbo_sync_status":
            "not_synced"
    }