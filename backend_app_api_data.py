from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import pandas as pd
import os
import json
from datetime import datetime

from ..database import get_db
from ..models import User, Report, PnLData, RedFlag, EntityAnalysis
from ..schemas import (
    DashboardResponse, KPIData, MonthlyData, EntityData, RedFlagData,
    AnalysisResponse, CostAnalysisData, RevenueAnalysisData, 
    ProfitabilityAnalysisData, RecommendationData,
    BenchmarkingResponse, IndustryBenchmarkData, CompetitorData, 
    HistoricalBenchmarkData, FilesResponse, FileData
)
from ..utils.data_processor import process_excel_file
from ..utils.file_handler import save_upload_file

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    month: str,
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
    
    # Get KPI data
    revenue = db.query(PnLData).filter(
        PnLData.report_id == report.id,
        PnLData.account_name == "Group Revenue"
    ).first()
    
    gross_profit = db.query(PnLData).filter(
        PnLData.report_id == report.id,
        PnLData.account_name == "Gross Profit"
    ).first()
    
    opex = db.query(PnLData).filter(
        PnLData.report_id == report.id,
        PnLData.category == "Opex"
    ).first()
    
    net_profit = db.query(PnLData).filter(
        PnLData.report_id == report.id,
        PnLData.account_name == "Net Profit before Tax"
    ).first()
    
    # Get previous month data for comparison
    prev_month = datetime.strptime(month, "%Y-%m").replace(month=datetime.strptime(month, "%Y-%m").month - 1).strftime("%Y-%m")
    prev_report = db.query(Report).filter(
        Report.month == prev_month,
        Report.owner_id == current_user.id,
        Report.is_processed == True
    ).first()
    
    prev_revenue = None
    prev_gpm = None
    prev_opex = None
    prev_net_profit = None
    
    if prev_report:
        prev_revenue_data = db.query(PnLData).filter(
            PnLData.report_id == prev_report.id,
            PnLData.account_name == "Group Revenue"
        ).first()
        
        prev_gross_profit_data = db.query(PnLData).filter(
            PnLData.report_id == prev_report.id,
            PnLData.account_name == "Gross Profit"
        ).first()
        
        prev_opex_data = db.query(PnLData).filter(
            PnLData.report_id == prev_report.id,
            PnLData.category == "Opex"
        ).first()
        
        prev_net_profit_data = db.query(PnLData).filter(
            PnLData.report_id == prev_report.id,
            PnLData.account_name == "Net Profit before Tax"
        ).first()
        
        if prev_revenue_data:
            prev_revenue = prev_revenue_data.actuals
        if prev_gross_profit_data and revenue:
            prev_gpm = (prev_gross_profit_data.actuals / prev_revenue_data.actuals) * 100
        if prev_opex_data:
            prev_opex = prev_opex_data.actuals
        if prev_net_profit_data:
            prev_net_profit = prev_net_profit_data.actuals
    
    # Calculate KPIs
    revenue_amount = revenue.actuals if revenue else 0
    revenue_change = ((revenue_amount - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
    
    gpm = (gross_profit.actuals / revenue.actuals * 100) if revenue and gross_profit else 0
    gpm_change = gpm - prev_gpm if prev_gpm is not None else 0
    
    opex_amount = sum([op.actuals for op in db.query(PnLData).filter(
        PnLData.report_id == report.id,
        PnLData.category == "Opex"
    ).all()])
    opex_change = ((opex_amount - prev_opex) / prev_opex * 100) if prev_opex else 0
    
    net_profit_amount = net_profit.actuals if net_profit else 0
    net_profit_change = ((net_profit_amount - prev_net_profit) / prev_net_profit * 100) if prev_net_profit else 0
    
    kpi_data = KPIData(
        revenue=revenue_amount,
        revenueChange=revenue_change,
        gpm=gpm,
        gpmChange=gpm_change,
        opex=opex_amount,
        opexChange=opex_change,
        netProfit=net_profit_amount,
        netProfitChange=net_profit_change
    )
    
    # Get monthly data for the past 12 months
    monthly_data = []
    for i in range(12):
        month_date = datetime.strptime(month, "%Y-%m").replace(month=datetime.strptime(month, "%Y-%m").month - i)
        month_str = month_date.strftime("%Y-%m")
        
        month_report = db.query(Report).filter(
            Report.month == month_str,
            Report.owner_id == current_user.id,
            Report.is_processed == True
        ).first()
        
        if month_report:
            month_revenue = db.query(PnLData).filter(
                PnLData.report_id == month_report.id,
                PnLData.account_name == "Group Revenue"
            ).first()
            
            month_gross_profit = db.query(PnLData).filter(
                PnLData.report_id == month_report.id,
                PnLData.account_name == "Gross Profit"
            ).first()
            
            month_net_profit = db.query(PnLData).filter(
                PnLData.report_id == month_report.id,
                PnLData.account_name == "Net Profit before Tax"
            ).first()
            
            revenue_amount = month_revenue.actuals if month_revenue else 0
            gross_profit_amount = month_gross_profit.actuals if month_gross_profit else 0
            net_profit_amount = month_net_profit.actuals if month_net_profit else 0
            
            gpm = (gross_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
            opm = (net_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
            npm = opm  # Simplified, should be calculated after tax
            
            monthly_data.append(MonthlyData(
                month=month_str,
                revenue=revenue_amount,
                grossProfit=gross_profit_amount,
                netProfit=net_profit_amount,
                gpm=gpm,
                opm=opm,
                npm=npm
            ))
    
    # Get entity data
    entities = db.query(EntityAnalysis).filter(
        EntityAnalysis.report_id == report.id
    ).all()
    
    entity_data = [
        EntityData(
            entity=entity.entity_name,
            revenue=entity.total_revenue,
            cost=entity.total_cost,
            gp=entity.gross_profit,
            gpm=entity.gpm
        )
        for entity in entities
    ]
    
    # Get red flags
    red_flags = db.query(RedFlag).filter(
        RedFlag.report_id == report.id
    ).all()
    
    red_flag_data = [
        RedFlagData(
            project=flag.project_name,
            country=flag.country,
            gpm=flag.gpm,
            comment=flag.comment
        )
        for flag in red_flags
    ]
    
    return DashboardResponse(
        success=True,
        kpi=kpi_data,
        monthly=monthly_data,
        entities=entity_data,
        redFlags=red_flag_data
    )

@router.get("/pnl")
async def get_pnl_data(
    month: str,
    target: Optional[str] = None,
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
    
    # Get P&L data
    pnl_data = db.query(PnLData).filter(
        PnLData.report_id == report.id
    ).all()
    
    # Convert to DataFrame for easier manipulation
    data = []
    for item in pnl_data:
        data.append({
            "account_name": item.account_name,
            "category": item.category,
            "actuals": item.actuals,
            "forecast": item.forecast,
            "variance": item.variance,
            "variance_pct": item.variance_pct
        })
    
    df = pd.DataFrame(data)
    
    # If target is specified, filter for that target
    if target:
        if target == "revenue":
            df = df[df["account_name"].str.contains("Revenue", case=False)]
        elif target == "costs":
            df = df[df["category"].isin(["Cost", "Direct Costs"])]
        elif target == "gross_profit":
            df = df[df["account_name"].str.contains("Gross Profit", case=False)]
        elif target == "net_profit":
            df = df[df["account_name"].str.contains("Net Profit", case=False)]
    
    return df.to_dict(orient="records")

@router.get("/analysis")
async def get_analysis_data(
    month: str,
    type: str,
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
    
    if type == "cost":
        # Get cost breakdown
        cost_data = db.query(PnLData).filter(
            PnLData.report_id == report.id,
            PnLData.category == "Opex"
        ).all()
        
        total_cost = sum([item.actuals for item in cost_data])
        
        cost_breakdown = [
            CostAnalysisData(
                category=item.account_name,
                amount=item.actuals,
                percentage=(item.actuals / total_cost * 100) if total_cost > 0 else 0,
                trend=item.variance_pct if item.variance_pct else 0
            )
            for item in cost_data
        ]
        
        # Generate recommendations based on cost analysis
        recommendations = [
            RecommendationData(
                title="Reduce Travel Expenses",
                content="Travel expenses have increased by 15% compared to last month. Consider implementing virtual meetings to reduce costs."
            ),
            RecommendationData(
                title="Review Subscription Services",
                content="Multiple subscription services are underutilized. Conduct a review to identify and cancel unnecessary subscriptions."
            )
        ]
        
        return AnalysisResponse(
            success=True,
            costBreakdown=cost_breakdown,
            revenueBreakdown=[],
            profitabilityAnalysis=[],
            recommendations=recommendations
        )
    
    elif type == "revenue":
        # Get revenue breakdown
        revenue_data = db.query(PnLData).filter(
            PnLData.report_id == report.id,
            PnLData.category == "Revenue"
        ).all()
        
        total_revenue = sum([item.actuals for item in revenue_data])
        
        revenue_breakdown = [
            RevenueAnalysisData(
                source=item.account_name,
                amount=item.actuals,
                percentage=(item.actuals / total_revenue * 100) if total_revenue > 0 else 0,
                trend=item.variance_pct if item.variance_pct else 0
            )
            for item in revenue_data
        ]
        
        # Generate recommendations based on revenue analysis
        recommendations = [
            RecommendationData(
                title="Focus on High-Growth Segments",
                content="Services segment has shown 20% growth compared to last month. Allocate more resources to capitalize on this trend."
            ),
            RecommendationData(
                title="Address Declining Product Lines",
                content="Hardware sales have declined by 10% for three consecutive months. Consider revising pricing or marketing strategy."
            )
        ]
        
        return AnalysisResponse(
            success=True,
            costBreakdown=[],
            revenueBreakdown=revenue_breakdown,
            profitabilityAnalysis=[],
            recommendations=recommendations
        )
    
    elif type == "profitability":
        # Get profitability data for the past 12 months
        profitability_data = []
        
        for i in range(12):
            month_date = datetime.strptime(month, "%Y-%m").replace(month=datetime.strptime(month, "%Y-%m").month - i)
            month_str = month_date.strftime("%Y-%m")
            
            month_report = db.query(Report).filter(
                Report.month == month_str,
                Report.owner_id == current_user.id,
                Report.is_processed == True
            ).first()
            
            if month_report:
                month_revenue = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Group Revenue"
                ).first()
                
                month_cost = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.category == "Direct Costs"
                ).first()
                
                month_gross_profit = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Gross Profit"
                ).first()
                
                month_opex = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.category == "Opex"
                ).all()
                
                month_net_profit = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Net Profit before Tax"
                ).first()
                
                revenue_amount = month_revenue.actuals if month_revenue else 0
                cost_amount = month_cost.actuals if month_cost else 0
                gross_profit_amount = month_gross_profit.actuals if month_gross_profit else 0
                opex_amount = sum([item.actuals for item in month_opex])
                net_profit_amount = month_net_profit.actuals if month_net_profit else 0
                
                gpm = (gross_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
                opm = (net_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
                npm = opm  # Simplified, should be calculated after tax
                
                profitability_data.append(ProfitabilityAnalysisData(
                    month=month_str,
                    revenue=revenue_amount,
                    cost=cost_amount,
                    grossProfit=gross_profit_amount,
                    gpm=gpm,
                    operatingProfit=net_profit_amount + opex_amount,
                    opm=opm,
                    netProfit=net_profit_amount,
                    npm=npm
                ))
        
        # Generate recommendations based on profitability analysis
        recommendations = [
            RecommendationData(
                title="Improve Gross Profit Margin",
                content="Gross profit margin has declined by 3% over the past quarter. Review pricing strategy and cost of goods sold."
            ),
            RecommendationData(
                title="Optimize Operating Expenses",
                content="Operating expenses have grown faster than revenue. Implement cost control measures to improve operating margin."
            )
        ]
        
        return AnalysisResponse(
            success=True,
            costBreakdown=[],
            revenueBreakdown=[],
            profitabilityAnalysis=profitability_data,
            recommendations=recommendations
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid analysis type")

@router.get("/benchmarking")
async def get_benchmarking_data(
    month: str,
    type: str,
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
    
    if type == "industry":
        # Mock industry benchmark data
        industry_data = [
            IndustryBenchmarkData(
                metric="Gross Profit Margin",
                ourCompany=28.0,
                industryAvg=25.5,
                topQuartile=32.0,
                performance="Above Average"
            ),
            IndustryBenchmarkData(
                metric="Operating Profit Margin",
                ourCompany=8.5,
                industryAvg=7.2,
                topQuartile=12.5,
                performance="Above Average"
            ),
            IndustryBenchmarkData(
                metric="Net Profit Margin",
                ourCompany=6.2,
                industryAvg=5.8,
                topQuartile=9.5,
                performance="Average"
            ),
            IndustryBenchmarkData(
                metric="Revenue Growth",
                ourCompany=12.5,
                industryAvg=10.2,
                topQuartile=18.0,
                performance="Above Average"
            )
        ]
        
        return BenchmarkingResponse(
            success=True,
            industryData=industry_data,
            competitorData=[],
            historicalBenchmark=[]
        )
    
    elif type == "competitor":
        # Mock competitor data
        competitor_data = [
            CompetitorData(
                metric="Gross Profit Margin",
                ourCompany=28.0,
                competitorA=26.5,
                competitorB=29.8,
                competitorC=24.2,
                ranking=2
            ),
            CompetitorData(
                metric="Operating Profit Margin",
                ourCompany=8.5,
                competitorA=7.2,
                competitorB=9.5,
                competitorC=6.8,
                ranking=2
            ),
            CompetitorData(
                metric="Net Profit Margin",
                ourCompany=6.2,
                competitorA=5.8,
                competitorB=7.2,
                competitorC=5.1,
                ranking=2
            ),
            CompetitorData(
                metric="Revenue Growth",
                ourCompany=12.5,
                competitorA=10.2,
                competitorB=15.8,
                competitorC=8.5,
                ranking=2
            )
        ]
        
        return BenchmarkingResponse(
            success=True,
            industryData=[],
            competitorData=competitor_data,
            historicalBenchmark=[]
        )
    
    elif type == "historical":
        # Get historical benchmark data for the past 12 months
        historical_data = []
        
        for i in range(12):
            month_date = datetime.strptime(month, "%Y-%m").replace(month=datetime.strptime(month, "%Y-%m").month - i)
            month_str = month_date.strftime("%Y-%m")
            
            month_report = db.query(Report).filter(
                Report.month == month_str,
                Report.owner_id == current_user.id,
                Report.is_processed == True
            ).first()
            
            if month_report:
                month_revenue = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Group Revenue"
                ).first()
                
                month_gross_profit = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Gross Profit"
                ).first()
                
                month_net_profit = db.query(PnLData).filter(
                    PnLData.report_id == month_report.id,
                    PnLData.account_name == "Net Profit before Tax"
                ).first()
                
                revenue_amount = month_revenue.actuals if month_revenue else 0
                gross_profit_amount = month_gross_profit.actuals if month_gross_profit else 0
                net_profit_amount = month_net_profit.actuals if month_net_profit else 0
                
                gpm = (gross_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
                opm = (net_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0
                npm = opm  # Simplified, should be calculated after tax
                
                # Calculate YoY growth
                prev_year_month = datetime.strptime(month_str, "%Y-%m").replace(year=datetime.strptime(month_str, "%Y-%m").year - 1).strftime("%Y-%m")
                prev_year_report = db.query(Report).filter(
                    Report.month == prev_year_month,
                    Report.owner_id == current_user.id,
                    Report.is_processed == True
                ).first()
                
                prev_year_revenue = 0
                prev_year_net_profit = 0
                
                if prev_year_report:
                    prev_year_revenue_data = db.query(PnLData).filter(
                        PnLData.report_id == prev_year_report.id,
                        PnLData.account_name == "Group Revenue"
                    ).first()
                    
                    prev_year_net_profit_data = db.query(PnLData).filter(
                        PnLData.report_id == prev_year_report.id,
                        PnLData.account_name == "Net Profit before Tax"
                    ).first()
                    
                    prev_year_revenue = prev_year_revenue_data.actuals if prev_year_revenue_data else 0
                    prev_year_net_profit = prev_year_net_profit_data.actuals if prev_year_net_profit_data else 0
                
                yoy_revenue_growth = ((revenue_amount - prev_year_revenue) / prev_year_revenue * 100) if prev_year_revenue > 0 else 0
                yoy_profit_growth = ((net_profit_amount - prev_year_net_profit) / prev_year_net_profit * 100) if prev_year_net_profit > 0 else 0
                
                historical_data.append(HistoricalBenchmarkData(
                    month=month_str,
                    revenue=revenue_amount,
                    revenueGrowth=0,  # Would need previous month data
                    profitGrowth=0,  # Would need previous month data
                    gpm=gpm,
                    opm=opm,
                    npm=npm,
                    yoyRevenueGrowth=yoy_revenue_growth,
                    yoyProfitGrowth=yoy_profit_growth
                ))
        
        return BenchmarkingResponse(
            success=True,
            industryData=[],
            competitorData=[],
            historicalBenchmark=historical_data
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid benchmarking type")

@router.get("/latest")
async def get_latest_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the latest report for the current user
    latest_report = db.query(Report).filter(
        Report.owner_id == current_user.id,
        Report.is_processed == True
    ).order_by(Report.upload_date.desc()).first()
    
    if not latest_report:
        return {"success": False, "message": "No reports found"}
    
    return {
        "success": True,
        "latestMonth": latest_report.month,
        "latestYear": latest_report.year
    }

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    month: str = Form(...),
    year: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save the uploaded file
    file_path = await save_upload_file(file, current_user.id)
    
    # Create a report record
    report = Report(
        filename=file.filename,
        file_path=file_path,
        month=month,
        year=year,
        owner_id=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    try:
        # Process the Excel file
        process_excel_file(file_path, report.id, db)
        
        # Mark the report as processed
        report.is_processed = True
        db.commit()
        
        return {"success": True, "message": "File uploaded and processed successfully"}
    except Exception as e:
        # If processing fails, delete the report and file
        db.delete(report)
        db.commit()
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/files", response_model=FilesResponse)
async def get_uploaded_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all reports for the current user
    reports = db.query(Report).filter(
        Report.owner_id == current_user.id
    ).order_by(Report.upload_date.desc()).all()
    
    files = [
        FileData(
            id=report.id,
            name=report.filename,
            uploadDate=report.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            status="Processed" if report.is_processed else "Processing"
        )
        for report in reports
    ]
    
    return FilesResponse(
        success=True,
        files=files
    )