from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
import json

from ..database import get_db
from ..models import User, Report, PnLData
from ..schemas import ChatRequest, ChatResponse

router = APIRouter()

# GLM-4.6 API configuration
GLM_API_URL = "https://api.z.ai/v1/chat/completions"
GLM_API_KEY = "your-glm-api-key"  # In production, use environment variables

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Prepare system message
        system_message = {
            "role": "system",
            "content": """You are a financial assistant for a management report application. You help users analyze financial data, understand trends, and make informed decisions.
            
            You have access to financial data including:
            - Revenue and profit metrics
            - Cost breakdowns
            - Entity performance
            - Red flags and issues
            - Predictions and forecasts
            
            When answering questions:
            1. Be concise and specific
            2. Provide data-driven insights
            3. Suggest actionable recommendations when appropriate
            4. If you don't have enough information, ask for clarification
            """
        }
        
        # Get the latest report for context
        latest_report = db.query(Report).filter(
            Report.owner_id == current_user.id,
            Report.is_processed == True
        ).order_by(Report.upload_date.desc()).first()
        
        context_message = None
        if latest_report:
            # Get key financial metrics from the latest report
            revenue = db.query(PnLData).filter(
                PnLData.report_id == latest_report.id,
                PnLData.account_name == "Group Revenue"
            ).first()
            
            gross_profit = db.query(PnLData).filter(
                PnLData.report_id == latest_report.id,
                PnLData.account_name == "Gross Profit"
            ).first()
            
            net_profit = db.query(PnLData).filter(
                PnLData.report_id == latest_report.id,
                PnLData.account_name == "Net Profit before Tax"
            ).first()
            
            context_info = f"Latest report from {latest_report.month}. "
            
            if revenue:
                context_info += f"Revenue: ${revenue.actuals:,.2f}. "
            
            if gross_profit and revenue:
                gpm = (gross_profit.actuals / revenue.actuals) * 100
                context_info += f"Gross Profit Margin: {gpm:.2f}%. "
            
            if net_profit and revenue:
                npm = (net_profit.actuals / revenue.actuals) * 100
                context_info += f"Net Profit Margin: {npm:.2f}%. "
            
            context_message = {
                "role": "system",
                "content": context_info
            }
        
        # Prepare messages for the API
        messages = [system_message]
        if context_message:
            messages.append(context_message)
        messages.extend(request.messages)
        
        # Call GLM-4.6 API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GLM_API_KEY}"
        }
        
        data = {
            "model": "glm-4",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(GLM_API_URL, headers=headers, json=data)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error calling GLM API")
        
        result = response.json()
        
        return ChatResponse(
            success=True,
            response=result["choices"][0]["message"]["content"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")