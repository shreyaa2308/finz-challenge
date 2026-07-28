async def save_correction(db, pattern, approved_account):
    await db.learned_mappings.update_one(
        {"pattern": pattern.upper()},
        {"$set": {"pattern": pattern.upper(), "approved_account": approved_account}},
        upsert=True
    )

async def get_learned_mapping(db, description):
    text = description.upper()
    cursor = db.learned_mappings.find()
    async for mapping in cursor:
        if mapping["pattern"] in text:
            return mapping["approved_account"]
    return None