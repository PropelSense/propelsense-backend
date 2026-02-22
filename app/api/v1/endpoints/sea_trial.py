"""
Sea Trial API Endpoints
RESTful API for sea trial management and analysis
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.sea_trial_service import SeaTrialService
from app.schemas.sea_trial import (
    SeaTrialCreate,
    SeaTrialUpdate,
    SeaTrialResponse,
    SeaTrialAnalysis,
    SeaTrialSummary,
    TrialStatus,
    MLPredictionResult
)
from app.models.sea_trial import SeaTrial

router = APIRouter()


def get_sea_trial_service(db: Session = Depends(get_db)) -> SeaTrialService:
    """Dependency to get sea trial service"""
    return SeaTrialService(db)


@router.post("/", response_model=SeaTrialResponse, status_code=201)
async def create_sea_trial(
    trial: SeaTrialCreate,
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Create a new sea trial
    
    - **trial_name**: Name or identifier for the trial
    - **vessel_name**: Name of the vessel being tested
    - **trial_date**: Date and time of the trial
    - **status**: Current status (planned, in_progress, completed, cancelled)
    - **predicted_***: Predicted performance values from model
    - **actual_***: Actual measured values during trial
    - **contract_***: Contract specification values
    """
    try:
        created_trial = service.create_trial(trial)
        return SeaTrialResponse.model_validate(created_trial)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sea trial: {str(e)}")


@router.get("/", response_model=List[SeaTrialResponse])
async def get_sea_trials(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[TrialStatus] = Query(None, description="Filter by trial status"),
    vessel_name: Optional[str] = Query(None, description="Filter by vessel name (partial match)"),
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Get list of sea trials with optional filtering
    
    - **skip**: Pagination offset
    - **limit**: Maximum results per page
    - **status**: Filter by trial status
    - **vessel_name**: Filter by vessel name (case-insensitive partial match)
    """
    trials = service.get_trials(skip=skip, limit=limit, status=status, vessel_name=vessel_name)
    return [SeaTrialResponse.model_validate(trial) for trial in trials]


@router.get("/summary", response_model=SeaTrialSummary)
async def get_sea_trials_summary(
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Get summary statistics for all sea trials
    
    Returns:
    - Total number of trials
    - Number of completed trials
    - Average performance score
    - Number of trials meeting contract specifications
    - Average deviations for speed, power, and fuel
    """
    return service.get_trials_summary()


@router.get("/{trial_id}", response_model=SeaTrialResponse)
async def get_sea_trial(
    trial_id: int,
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Get a specific sea trial by ID
    
    - **trial_id**: Unique identifier of the sea trial
    """
    trial = service.get_trial(trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail=f"Sea trial {trial_id} not found")
    
    return SeaTrialResponse.model_validate(trial)


@router.get("/{trial_id}/analysis", response_model=SeaTrialAnalysis)
async def get_sea_trial_analysis(
    trial_id: int,
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Get comprehensive performance analysis for a sea trial
    
    Returns detailed comparison between predicted and actual performance:
    - Speed comparison
    - Power comparison
    - Fuel consumption comparison
    - RPM comparison
    - Overall performance score
    - Contract compliance status
    - Summary and recommendations
    """
    analysis = service.get_trial_analysis(trial_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Sea trial {trial_id} not found")
    
    return analysis


@router.put("/{trial_id}", response_model=SeaTrialResponse)
async def update_sea_trial(
    trial_id: int,
    trial_update: SeaTrialUpdate,
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Update an existing sea trial
    
    Only provided fields will be updated. All fields are optional.
    Performance analysis is automatically recalculated after update.
    """
    updated_trial = service.update_trial(trial_id, trial_update)
    if not updated_trial:
        raise HTTPException(status_code=404, detail=f"Sea trial {trial_id} not found")
    
    return SeaTrialResponse.model_validate(updated_trial)


@router.delete("/{trial_id}", status_code=204)
async def delete_sea_trial(
    trial_id: int,
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Delete a sea trial
    
    - **trial_id**: Unique identifier of the sea trial to delete
    """
    success = service.delete_trial(trial_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sea trial {trial_id} not found")
    
    return None


@router.post("/{trial_id}/ml-predict", response_model=MLPredictionResult)
async def run_ml_prediction(
    trial_id: int,
    update_trial: bool = Query(True, description="Save ML prediction to trial's predicted_power field"),
    service: SeaTrialService = Depends(get_sea_trial_service)
):
    """
    Run the integrated XGBoost ML model on a sea trial's environmental conditions
    to generate a power prediction.

    The model maps the trial's measured vessel and environmental data to the
    trained feature set:
    - Speed through water (actual_speed)
    - Draft (fore + aft)
    - Wind speed/direction → U/V components
    - Current speed/direction → U/V components
    - Wave height
    - Time since dry dock

    If **update_trial** is True (default), the result is saved back to
    `predicted_power` on the trial and deviations are recalculated.

    **Requirements**: trial must have `actual_speed`, `draft_fore`, and `draft_aft`
    set, otherwise a 422 error is returned.
    """
    try:
        result = service.run_ml_prediction(trial_id, update_trial=update_trial)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Sea trial {trial_id} not found")
    return result
