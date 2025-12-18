from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Report schemas
class ReportBase(BaseModel):
    filename: str
    month: str
    year: int

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    file_path: str
    upload_date: datetime
    is_processed: bool
    owner_id: int
    
    class Config:
        orm_mode = True

# P&L Data schemas
class PnLDataBase(BaseModel):
    account_name: str
    category: str
    month: str
    actuals: float
    forecast: Optional[float] = None
    variance: Optional[float] = None
    variance_pct: Optional[float] = None

class PnLDataCreate(PnLDataBase):
    report_id: int

class PnLData(PnLDataBase):
    id: int
    report_id: int
    
    class Config:
        orm_mode = True

# Prediction schemas
class PredictionRequest(BaseModel):
    target: str
    periods: int
    model_type: str
    scenario: str = "baseline"
    month: Optional[str] = None

class PredictionResponse(BaseModel):
    success: bool
    predictions: List[float]
    confidence_intervals: List[List[float]]
    model_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None

# Dashboard schemas
class KPIData(BaseModel):
    revenue: float
    revenueChange: float
    gpm: float
    gpmChange: float
    opex: float
    opexChange: float
    netProfit: float
    netProfitChange: float

class MonthlyData(BaseModel):
    month: str
    revenue: float
    grossProfit: float
    netProfit: float
    gpm: float
    opm: float
    npm: float

class EntityData(BaseModel):
    entity: str
    revenue: float
    cost: float
    gp: float
    gpm: float

class RedFlagData(BaseModel):
    project: str
    country: str
    gpm: float
    comment: str

class DashboardResponse(BaseModel):
    success: bool
    kpi: KPIData
    monthly: List[MonthlyData]
    entities: List[EntityData]
    redFlags: List[RedFlagData]

# Analysis schemas
class CostAnalysisData(BaseModel):
    category: str
    amount: float
    percentage: float
    trend: float

class RevenueAnalysisData(BaseModel):
    source: str
    amount: float
    percentage: float
    trend: float

class ProfitabilityAnalysisData(BaseModel):
    month: str
    revenue: float
    cost: float
    grossProfit: float
    gpm: float
    operatingProfit: float
    opm: float
    netProfit: float
    npm: float

class RecommendationData(BaseModel):
    title: str
    content: str

class AnalysisResponse(BaseModel):
    success: bool
    costBreakdown: List[CostAnalysisData]
    revenueBreakdown: List[RevenueAnalysisData]
    profitabilityAnalysis: List[ProfitabilityAnalysisData]
    recommendations: List[RecommendationData]

# Benchmarking schemas
class IndustryBenchmarkData(BaseModel):
    metric: str
    ourCompany: float
    industryAvg: float
    topQuartile: float
    performance: str

class CompetitorData(BaseModel):
    metric: str
    ourCompany: float
    competitorA: float
    competitorB: float
    competitorC: float
    ranking: int

class HistoricalBenchmarkData(BaseModel):
    month: str
    revenue: float
    revenueGrowth: float
    profitGrowth: float
    gpm: float
    opm: float
    npm: float
    yoyRevenueGrowth: float
    yoyProfitGrowth: float

class BenchmarkingResponse(BaseModel):
    success: bool
    industryData: List[IndustryBenchmarkData]
    competitorData: List[CompetitorData]
    historicalBenchmark: List[HistoricalBenchmarkData]

# Chat schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    success: bool
    response: str

# File schemas
class FileData(BaseModel):
    id: int
    name: str
    uploadDate: str
    status: str

class FilesResponse(BaseModel):
    success: bool
    files: List[FileData]