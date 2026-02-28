"""
Reports endpoints
Generate and manage PDF reports for predictions and sea trials
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.database import get_db
from app.core.auth import require_auth
from app.models.report import Report
from app.schemas.report import ReportResponse, ReportListResponse, GenerateReportRequest
from app.services import report_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_TYPES = {"prediction_summary", "sea_trial_summary"}
TYPE_LABELS = {
    "prediction_summary": "Power Prediction Summary",
    "sea_trial_summary":  "Sea Trial Performance Report",
}


@router.get("/", response_model=ReportListResponse, summary="List user reports")
async def list_reports(
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(Report)
        .filter(Report.user_id == user["id"])
        .order_by(Report.created_at.desc())
        .all()
    )
    return ReportListResponse(reports=reports, total=len(reports))


@router.post("/generate", response_model=ReportResponse, summary="Generate a report")
async def generate_report(
    req: GenerateReportRequest,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if req.report_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown report type: {req.report_type}")

    title = req.title or TYPE_LABELS[req.report_type]
    record = Report(
        user_id=user["id"],
        user_email=user.get("email"),
        title=title,
        report_type=req.report_type,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{report_id}/download", summary="Download report PDF")
async def download_report(
    report_id: int,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
):
    record = db.query(Report).filter(Report.id == report_id, Report.user_id == user["id"]).first()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        if record.report_type == "prediction_summary":
            pdf_bytes = report_service.generate_prediction_summary(db, user["id"], user.get("email", ""))
        elif record.report_type == "sea_trial_summary":
            pdf_bytes = report_service.generate_sea_trial_summary(db, user.get("email", ""))
        else:
            raise HTTPException(status_code=400, detail="Unknown report type")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed")

    filename = f"{record.report_type}_{record.id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a report")
async def delete_report(
    report_id: int,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db),
):
    record = db.query(Report).filter(Report.id == report_id, Report.user_id == user["id"]).first()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(record)
    db.commit()
