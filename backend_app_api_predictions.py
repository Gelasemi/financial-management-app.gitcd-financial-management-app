from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import numpy as np

from ..database import get_db
from ..models import User, Report, PnLData, Prediction
from ..schemas import PredictionRequest, PredictionResponse
from ..ml.prediction_pipeline import generate_financial_predictions

router = APIRouter()

@router.post("/pnl", response_model=PredictionResponse)
async def predict_pnl(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the report for the specified month
    report = db.query(Report).filter(
        Report.month == request.month,
        Report.owner_id == current_user.id,
        Report.is_processed == True
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Generate predictions using the ML pipeline
        predictions, confidence_intervals, model_metrics, feature_importance = generate_financial_predictions(
            report_id=report.id,
            target=request.target,
            periods=request.periods,
            model_type=request.model_type,
            scenario=request.scenario,
            db=db
        )
        
        # Save the prediction to the database
        prediction = Prediction(
            report_id=report.id,
            target=request.target,
            model_type=request.model_type,
            scenario=request.scenario,
            periods=request.periods,
            predictions=json.dumps(predictions),
            confidence_intervals=json.dumps(confidence_intervals),
            model_metrics=json.dumps(model_metrics),
            feature_importance=json.dumps(feature_importance) if feature_importance else None
        )
        db.add(prediction)
        db.commit()
        
        return PredictionResponse(
            success=True,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            model_metrics=model_metrics,
            feature_importance=feature_importance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@router.get("/balance-sheet")
async def predict_balance_sheet(
    month: str,
    periods: int = 6,
    model_type: str = "xgboost",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the report for the specified month
    report = db.query(Report).filter(
        Report.month == month,
        Report.owner_id == current_user.id,
        Report.is_processed == True
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Generate balance sheet predictions
        # This is a placeholder for balance sheet prediction logic
        assets_predictions = np.random.normal(1000000, 100000, periods).tolist()
        liabilities_predictions = np.random.normal(600000, 80000, periods).tolist()
        equity_predictions = [a - l for a, l in zip(assets_predictions, liabilities_predictions)]
        
        return {
            "success": True,
            "assets": assets_predictions,
            "liabilities": liabilities_predictions,
            "equity": equity_predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating balance sheet predictions: {str(e)}")

@router.get("/history")
async def get_prediction_history(
    month: str,
    target: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the report for the specified month
    report = db.query(Report).filter(
        Report.month == month,
        Report.owner_id == current_user.id,
        Report.is_processed == True
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get all predictions for the specified target
    predictions = db.query(Prediction).filter(
        Prediction.report_id == report.id,
        Prediction.target == target
    ).all()
    
    prediction_history = []
    for pred in predictions:
        prediction_history.append({
            "id": pred.id,
            "model_type": pred.model_type,
            "scenario": pred.scenario,
            "periods": pred.periods,
            "prediction_date": pred.prediction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "predictions": json.loads(pred.predictions),
            "confidence_intervals": json.loads(pred.confidence_intervals),
            "model_metrics": json.loads(pred.model_metrics),
            "feature_importance": json.loads(pred.feature_importance) if pred.feature_importance else None
        })
    
    return {
        "success": True,
        "predictions": prediction_history
    }