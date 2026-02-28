"""
Report Model
Stores metadata for generated reports (PDFs are generated on-demand)
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # User association
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=True)

    # Report info
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # "prediction_summary" | "sea_trial_summary"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<Report(id={self.id}, type={self.report_type}, user={self.user_email})>"
