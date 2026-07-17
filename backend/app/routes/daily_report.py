"""Daily Report API — get today's report, trigger send to Telegram"""
from fastapi import APIRouter
from modules.daily_report import generate_today_report, format_report_text

router = APIRouter(prefix="", tags=["Daily Report"])

@router.get("/daily-report")
async def get_daily_report():
    """Get today's email campaign report"""
    report = generate_today_report()
    return {"success": True, "data": report}

@router.get("/daily-report/text")
async def get_daily_report_text():
    """Get today's report as plain text"""
    report = generate_today_report()
    text = format_report_text(report)
    return {"success": True, "data": {"text": text}}
