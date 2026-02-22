"""
Sea Trial Service - Business Logic Layer
Handles calculations and analysis for sea trial performance
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import math

from app.models.sea_trial import SeaTrial, TrialStatus
from app.schemas.sea_trial import (
    SeaTrialCreate,
    SeaTrialUpdate,
    SeaTrialResponse,
    PerformanceComparison,
    SeaTrialAnalysis,
    SeaTrialSummary,
    MLPredictionResult
)
from app.services.ml_service import get_ml_service

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
    
    def predict_from_ml(self, trial: SeaTrial) -> tuple[Optional[float], dict]:
        """
        Run the XGBoost ML model on a sea trial's environmental conditions
        to predict shaft power in kW.

        Maps sea trial fields → ML VesselFeatures:
          - draft_aft / draft_fore  → draft_aft_telegram / draft_fore_telegram
          - actual_speed (knots)    → stw
          - wind_speed + direction  → awind_ucomp_provider / awind_vcomp_provider  (m/s)
          - current_speed + dir     → rcurrent_ucomp / rcurrent_vcomp              (m/s)
          - wave_height             → comb_wind_swell_wave_height
          - time_since_dry_dock     → timeSinceDryDock

        Returns:
            Tuple of (predicted_power_kw, features_used_dict) or (None, {})
        """
        stw = trial.actual_speed
        draft_aft = trial.draft_aft
        draft_fore = trial.draft_fore

        if stw is None or draft_aft is None or draft_fore is None:
            logger.warning(
                f"Missing required ML features (stw/draft) for trial {trial.sea_trial_id}"
            )
            return None, {}

        # Convert knots → m/s  (1 knot = 0.514444 m/s)
        KNOTS_TO_MS = 0.514444

        wind_speed_ms = (trial.wind_speed or 0.0) * KNOTS_TO_MS
        wind_dir_rad = math.radians(trial.wind_direction or 0.0)
        awind_ucomp = wind_speed_ms * math.cos(wind_dir_rad)
        awind_vcomp = wind_speed_ms * math.sin(wind_dir_rad)

        current_speed_ms = (trial.current_speed or 0.0) * KNOTS_TO_MS
        current_dir_rad = math.radians(trial.current_direction or 0.0)
        rcurrent_ucomp = current_speed_ms * math.cos(current_dir_rad)
        rcurrent_vcomp = current_speed_ms * math.sin(current_dir_rad)

        features = {
            "draft_aft_telegram": float(draft_aft),
            "draft_fore_telegram": float(draft_fore),
            "stw": float(stw),
            "diff_speed_overground": 0.0,
            "awind_vcomp_provider": awind_vcomp,
            "awind_ucomp_provider": awind_ucomp,
            "rcurrent_vcomp": rcurrent_vcomp,
            "rcurrent_ucomp": rcurrent_ucomp,
            "comb_wind_swell_wave_height": float(trial.wave_height or 0.0),
            "timeSinceDryDock": float(trial.time_since_dry_dock or 0.0),
        }

        try:
            ml_service = get_ml_service()
            predicted_kw, _ = ml_service.predict(features)
            return float(predicted_kw), features
        except Exception as e:
            logger.error(f"ML prediction failed for trial {trial.sea_trial_id}: {e}")
            return None, features

    def run_ml_prediction(self, trial_id: int, update_trial: bool = True) -> Optional[MLPredictionResult]:
        """
        Run the ML model for a sea trial and optionally persist the predicted_power.

        Args:
            trial_id: Sea trial to predict for
            update_trial: If True, save the ML result to trial.predicted_power

        Returns:
            MLPredictionResult or None if trial not found
        """
        trial = self.get_trial(trial_id)
        if not trial:
            return None

        predicted_kw, features_used = self.predict_from_ml(trial)

        if predicted_kw is None:
            raise ValueError(
                "Cannot run ML prediction: trial is missing required fields "
                "(actual_speed, draft_fore, draft_aft)."
            )

        if update_trial:
            trial.predicted_power = predicted_kw
            trial = self.update_trial_analysis(trial)
            self.db.commit()
            self.db.refresh(trial)
            logger.info(
                f"ML prediction saved to trial {trial_id}: {predicted_kw:.1f} kW"
            )

        return MLPredictionResult(
            sea_trial_id=trial_id,
            predicted_power_kw=round(predicted_kw, 2),
            predicted_power_mw=round(predicted_kw / 1000, 4),
            updated=update_trial,
            message=(
                f"ML model predicted {predicted_kw:.1f} kW shaft power."
                + (" Trial updated." if update_trial else " Trial not updated (dry-run).")
            ),
            features_used=features_used,
            trial=SeaTrialResponse.model_validate(trial) if update_trial else None,
        )

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
