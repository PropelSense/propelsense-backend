"""
Sea Trial Service - Business Logic Layer
Handles calculations and analysis for sea trial performance
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.sea_trial import SeaTrial, TrialStatus
from app.schemas.sea_trial import (
    SeaTrialCreate,
    SeaTrialUpdate,
    SeaTrialResponse,
    PerformanceComparison,
    SeaTrialAnalysis,
    SeaTrialSummary
)

logger = logging.getLogger(__name__)


class SeaTrialService:
    """Service for sea trial data management and analysis"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
    
    def calculate_deviation(self, predicted: Optional[float], actual: Optional[float]) -> Optional[float]:
        """
        Calculate percentage deviation between predicted and actual values
        
        Args:
            predicted: Predicted value
            actual: Actual measured value
            
        Returns:
            Percentage deviation (negative = actual is less than predicted)
        """
        if predicted is None or actual is None or predicted == 0:
            return None
        
        return ((actual - predicted) / predicted) * 100
    
    def calculate_performance_score(self, trial: SeaTrial) -> float:
        """
        Calculate overall performance score (0-100)
        Higher is better. Based on deviations from predicted values.
        
        Score breakdown:
        - Speed deviation: 40%
        - Power deviation: 40%
        - Fuel deviation: 20%
        """
        scores = []
        weights = []
        
        # Speed score (closer to predicted = higher score)
        if trial.speed_deviation is not None:
            speed_score = max(0, 100 - abs(trial.speed_deviation) * 10)
            scores.append(speed_score)
            weights.append(0.4)
        
        # Power score (lower is better, but close to predicted is ideal)
        if trial.power_deviation is not None:
            power_score = max(0, 100 - abs(trial.power_deviation) * 10)
            scores.append(power_score)
            weights.append(0.4)
        
        # Fuel score (lower is better)
        if trial.fuel_deviation is not None:
            fuel_score = max(0, 100 - abs(trial.fuel_deviation) * 10)
            scores.append(fuel_score)
            weights.append(0.2)
        
        if not scores:
            return 0.0
        
        # Weighted average
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)
        
        return round(weighted_sum / total_weight, 2)
    
    def check_contract_compliance(self, trial: SeaTrial) -> bool:
        """
        Check if trial meets contract specifications
        
        Contract is met if:
        - Actual speed >= contract speed (or within 2%)
        - Actual power <= contract power (or within 5%)
        - Actual fuel <= contract fuel (or within 5%)
        """
        checks = []
        
        if trial.contract_speed and trial.actual_speed:
            speed_ok = trial.actual_speed >= (trial.contract_speed * 0.98)
            checks.append(speed_ok)
        
        if trial.contract_power and trial.actual_power:
            power_ok = trial.actual_power <= (trial.contract_power * 1.05)
            checks.append(power_ok)
        
        if trial.contract_fuel and trial.actual_fuel_consumption:
            fuel_ok = trial.actual_fuel_consumption <= (trial.contract_fuel * 1.05)
            checks.append(fuel_ok)
        
        # All checks must pass
        return all(checks) if checks else False
    
    def update_trial_analysis(self, trial: SeaTrial) -> SeaTrial:
        """
        Update calculated fields for a sea trial
        
        Args:
            trial: SeaTrial object to update
            
        Returns:
            Updated SeaTrial object
        """
        # Calculate deviations
        trial.speed_deviation = self.calculate_deviation(trial.predicted_speed, trial.actual_speed)
        trial.power_deviation = self.calculate_deviation(trial.predicted_power, trial.actual_power)
        trial.fuel_deviation = self.calculate_deviation(trial.predicted_fuel_consumption, trial.actual_fuel_consumption)
        
        # Calculate overall performance score
        trial.overall_performance_score = self.calculate_performance_score(trial)
        
        # Check contract compliance
        trial.meets_contract = 1 if self.check_contract_compliance(trial) else 0
        
        return trial
    
    def create_trial(self, trial_data: SeaTrialCreate) -> SeaTrial:
        """Create a new sea trial"""
        trial = SeaTrial(**trial_data.model_dump())
        trial = self.update_trial_analysis(trial)
        
        self.db.add(trial)
        self.db.commit()
        self.db.refresh(trial)
        
        logger.info(f"Created sea trial: {trial.trial_name} (ID: {trial.sea_trial_id})")
        return trial
    
    def get_trial(self, trial_id: int) -> Optional[SeaTrial]:
        """Get a single sea trial by ID"""
        return self.db.query(SeaTrial).filter(SeaTrial.sea_trial_id == trial_id).first()
    
    def get_trials(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TrialStatus] = None,
        vessel_name: Optional[str] = None
    ) -> List[SeaTrial]:
        """Get list of sea trials with optional filtering"""
        query = self.db.query(SeaTrial)
        
        if status:
            query = query.filter(SeaTrial.status == status)
        
        if vessel_name:
            query = query.filter(SeaTrial.vessel_name.ilike(f"%{vessel_name}%"))
        
        return query.order_by(SeaTrial.trial_date.desc()).offset(skip).limit(limit).all()
    
    def update_trial(self, trial_id: int, trial_update: SeaTrialUpdate) -> Optional[SeaTrial]:
        """Update an existing sea trial"""
        trial = self.get_trial(trial_id)
        if not trial:
            return None
        
        # Update fields
        update_data = trial_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trial, field, value)
        
        # Recalculate analysis
        trial = self.update_trial_analysis(trial)
        
        self.db.commit()
        self.db.refresh(trial)
        
        logger.info(f"Updated sea trial: {trial.trial_name} (ID: {trial.sea_trial_id})")
        return trial
    
    def delete_trial(self, trial_id: int) -> bool:
        """Delete a sea trial"""
        trial = self.get_trial(trial_id)
        if not trial:
            return False
        
        self.db.delete(trial)
        self.db.commit()
        
        logger.info(f"Deleted sea trial ID: {trial_id}")
        return True
    
    def get_trial_analysis(self, trial_id: int) -> Optional[SeaTrialAnalysis]:
        """Get comprehensive analysis for a sea trial"""
        trial = self.get_trial(trial_id)
        if not trial:
            return None
        
        # Build performance comparisons
        speed_comp = PerformanceComparison(
            metric="Speed",
            predicted=trial.predicted_speed,
            actual=trial.actual_speed,
            deviation=trial.speed_deviation,
            deviation_absolute=trial.actual_speed - trial.predicted_speed if trial.actual_speed and trial.predicted_speed else None,
            unit="knots",
            status=self._get_deviation_status(trial.speed_deviation, "speed")
        )
        
        power_comp = PerformanceComparison(
            metric="Power",
            predicted=trial.predicted_power,
            actual=trial.actual_power,
            deviation=trial.power_deviation,
            deviation_absolute=trial.actual_power - trial.predicted_power if trial.actual_power and trial.predicted_power else None,
            unit="kW",
            status=self._get_deviation_status(trial.power_deviation, "power")
        )
        
        fuel_comp = PerformanceComparison(
            metric="Fuel Consumption",
            predicted=trial.predicted_fuel_consumption,
            actual=trial.actual_fuel_consumption,
            deviation=trial.fuel_deviation,
            deviation_absolute=trial.actual_fuel_consumption - trial.predicted_fuel_consumption if trial.actual_fuel_consumption and trial.predicted_fuel_consumption else None,
            unit="tonnes/day",
            status=self._get_deviation_status(trial.fuel_deviation, "fuel")
        )
        
        rpm_comp = PerformanceComparison(
            metric="RPM",
            predicted=trial.predicted_rpm,
            actual=trial.actual_rpm,
            deviation=self.calculate_deviation(trial.predicted_rpm, trial.actual_rpm),
            deviation_absolute=trial.actual_rpm - trial.predicted_rpm if trial.actual_rpm and trial.predicted_rpm else None,
            unit="RPM",
            status=self._get_deviation_status(self.calculate_deviation(trial.predicted_rpm, trial.actual_rpm), "rpm")
        )
        
        # Generate summary and recommendations
        summary = self._generate_summary(trial)
        recommendations = self._generate_recommendations(trial)
        
        return SeaTrialAnalysis(
            sea_trial_id=trial.sea_trial_id,
            trial_name=trial.trial_name,
            vessel_name=trial.vessel_name,
            trial_date=trial.trial_date,
            status=trial.status,
            speed_comparison=speed_comp,
            power_comparison=power_comp,
            fuel_comparison=fuel_comp,
            rpm_comparison=rpm_comp,
            overall_performance_score=trial.overall_performance_score or 0,
            meets_contract=bool(trial.meets_contract),
            summary=summary,
            recommendations=recommendations
        )
    
    def get_trials_summary(self) -> SeaTrialSummary:
        """Get summary statistics for all sea trials"""
        total = self.db.query(func.count(SeaTrial.sea_trial_id)).scalar()
        completed = self.db.query(func.count(SeaTrial.sea_trial_id)).filter(
            SeaTrial.status == TrialStatus.COMPLETED
        ).scalar()
        
        # Calculate averages for completed trials
        completed_trials = self.db.query(SeaTrial).filter(
            SeaTrial.status == TrialStatus.COMPLETED
        ).all()
        
        avg_score = None
        avg_speed_dev = None
        avg_power_dev = None
        avg_fuel_dev = None
        meeting_contract = 0
        
        if completed_trials:
            scores = [t.overall_performance_score for t in completed_trials if t.overall_performance_score is not None]
            speed_devs = [t.speed_deviation for t in completed_trials if t.speed_deviation is not None]
            power_devs = [t.power_deviation for t in completed_trials if t.power_deviation is not None]
            fuel_devs = [t.fuel_deviation for t in completed_trials if t.fuel_deviation is not None]
            
            avg_score = sum(scores) / len(scores) if scores else None
            avg_speed_dev = sum(speed_devs) / len(speed_devs) if speed_devs else None
            avg_power_dev = sum(power_devs) / len(power_devs) if power_devs else None
            avg_fuel_dev = sum(fuel_devs) / len(fuel_devs) if fuel_devs else None
            
            meeting_contract = sum(1 for t in completed_trials if t.meets_contract == 1)
        
        return SeaTrialSummary(
            total_trials=total or 0,
            completed_trials=completed or 0,
            avg_performance_score=round(avg_score, 2) if avg_score else None,
            trials_meeting_contract=meeting_contract,
            avg_speed_deviation=round(avg_speed_dev, 2) if avg_speed_dev else None,
            avg_power_deviation=round(avg_power_dev, 2) if avg_power_dev else None,
            avg_fuel_deviation=round(avg_fuel_dev, 2) if avg_fuel_dev else None
        )
    
    def _get_deviation_status(self, deviation: Optional[float], metric_type: str) -> str:
        """Determine status based on deviation"""
        if deviation is None:
            return "unknown"
        
        abs_dev = abs(deviation)
        
        # For power and fuel, lower is better
        if metric_type in ["power", "fuel"]:
            if deviation < -5:
                return "better"  # Using less than predicted
            elif deviation > 5:
                return "worse"  # Using more than predicted
            else:
                return "within_tolerance"
        
        # For speed and rpm, closer to predicted is better
        if abs_dev <= 2:
            return "within_tolerance"
        elif abs_dev <= 5:
            return "acceptable"
        else:
            return "needs_attention"
    
    def _generate_summary(self, trial: SeaTrial) -> str:
        """Generate text summary of trial results"""
        if trial.status != TrialStatus.COMPLETED:
            return f"Trial is currently {trial.status.value}"
        
        score = trial.overall_performance_score or 0
        meets = "meets" if trial.meets_contract else "does not meet"
        
        return f"Sea trial completed with performance score of {score:.1f}/100. Vessel {meets} contract specifications."
    
    def _generate_recommendations(self, trial: SeaTrial) -> List[str]:
        """Generate recommendations based on trial results"""
        recommendations = []
        
        if trial.speed_deviation and abs(trial.speed_deviation) > 5:
            if trial.speed_deviation > 0:
                recommendations.append("Speed exceeded predictions - verify propulsion efficiency")
            else:
                recommendations.append("Speed below predictions - investigate hull fouling or propulsion issues")
        
        if trial.power_deviation and trial.power_deviation > 10:
            recommendations.append("Power consumption higher than predicted - optimize propulsion system")
        
        if trial.fuel_deviation and trial.fuel_deviation > 10:
            recommendations.append("Fuel consumption higher than predicted - review engine tuning")
        
        if not trial.meets_contract:
            recommendations.append("Contract specifications not met - consider corrective actions")
        
        if trial.overall_performance_score and trial.overall_performance_score > 90:
            recommendations.append("Excellent performance - document best practices")
        
        if not recommendations:
            recommendations.append("Performance within acceptable parameters")
        
        return recommendations
