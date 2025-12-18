from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    reports = relationship("Report", back_populates="owner")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    month = Column(String)  # Format: "YYYY-MM"
    year = Column(Integer)
    is_processed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="reports")
    pnl_data = relationship("PnLData", back_populates="report")
    predictions = relationship("Prediction", back_populates="report")

class PnLData(Base):
    __tablename__ = "pnl_data"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    account_name = Column(String)
    category = Column(String)  # revenue, cost, opex, etc.
    month = Column(String)  # Format: "YYYY-MM"
    actuals = Column(Float)
    forecast = Column(Float)
    variance = Column(Float)
    variance_pct = Column(Float)
    
    report = relationship("Report", back_populates="pnl_data")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    target = Column(String)  # revenue, cost, profit, etc.
    model_type = Column(String)  # arima, xgboost, lstm, prophet
    scenario = Column(String)  # baseline, optimistic, pessimistic
    periods = Column(Integer)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    predictions = Column(Text)  # JSON string of predictions
    confidence_intervals = Column(Text)  # JSON string of confidence intervals
    model_metrics = Column(Text)  # JSON string of model metrics
    feature_importance = Column(Text)  # JSON string of feature importance
    
    report = relationship("Report", back_populates="predictions")

class RedFlag(Base):
    __tablename__ = "red_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    project_name = Column(String)
    country = Column(String)
    gpm = Column(Float)  # Gross Profit Margin
    comment = Column(Text)
    
    report = relationship("Report")

class EntityAnalysis(Base):
    __tablename__ = "entity_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    entity_name = Column(String)
    local_revenue = Column(Float)
    interco_revenue = Column(Float)
    total_revenue = Column(Float)
    local_cost = Column(Float)
    interco_cost = Column(Float)
    total_cost = Column(Float)
    gross_profit = Column(Float)
    gpm = Column(Float)  # Gross Profit Margin
    comment = Column(Text)
    
    report = relationship("Report")