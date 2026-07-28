def rule_based_classify(description):
    text = description.upper()
    if "OWNER CAPITAL" in text:
        return {"transaction_type": "owner_activity"}
    if "TRANSFER" in text:
        return {"transaction_type": "transfer"}
    if "GOOGLE ADS" in text:
        return {
            "transaction_type": "operating_expense",
            "account_name": "Marketing & Advertising"
        }
    return None