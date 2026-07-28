from fastapi import APIRouter
from backend.app.db.mongodb import get_database
from backend.app.services.qbo_sync import sync_all_approved

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.post("/run")
async def run_sync():
    db = get_database()
    results = await sync_all_approved(db)
    return {"results": results}