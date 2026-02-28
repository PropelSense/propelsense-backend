"""
Report Schemas
Pydantic models for report API
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    report_type: str
    created_at: datetime
    user_email: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
    total: int


class GenerateReportRequest(BaseModel):
    report_type: str   # "prediction_summary" | "sea_trial_summary"
    title: Optional[str] = None
