from fastapi import APIRouter
from backend.app.db.mongodb import get_database
from backend.app.services.pnl_service import generate_pnl

router = APIRouter(prefix="/pnl", tags=["P&L"])

@router.get("/{month}")
async def get_pnl(month: str):
    ranges = {
        "april": ("2026-04-01", "2026-04-30"),
        "may": ("2026-05-01", "2026-05-31"),
        "june": ("2026-06-01", "2026-06-30"),
        "quarter": ("2026-04-01", "2026-06-30")
    }
    start, end = ranges[month]
    db = get_database()
    return await generate_pnl(db, start, end)