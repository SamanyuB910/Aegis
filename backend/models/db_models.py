from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import uuid
from datetime import datetime
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraudx_copilot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Transaction(Base):
    """Transaction model for storing financial transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    txn_id = Column(String, unique=True, index=True, default=lambda: f"TXN-{uuid.uuid4().hex[:8].upper()}")
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_id = Column(String, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    category = Column(String, index=True)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Fraud detection fields
    fraud_score = Column(Float, default=0.0)
    graph_risk_score = Column(Float, default=0.0)
    is_flagged = Column(Boolean, default=False, index=True)
    status = Column(String, default="pending")  # pending, cleared, flagged, reviewing
    
    # Analysis results
    anomaly_factors = Column(JSON)  # Store ML model factors
    explanation = Column(Text)  # Human-readable explanation
    
    # Metadata
    transaction_metadata = Column(JSON)  # Additional transaction data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User model for account holders"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    risk_profile = Column(String, default="low")  # low, medium, high
    account_age_days = Column(Integer, default=0)
    
    # Risk scoring
    historical_fraud_score = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Receipt(Base):
    """Receipt model for document analysis"""
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(String, unique=True, index=True, default=lambda: f"RCP-{uuid.uuid4().hex[:8].upper()}")
    transaction_id = Column(String, index=True)  # Link to transaction
    
    # File information
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    content_type = Column(String)
    
    # OCR results
    ocr_text = Column(Text)
    extracted_amount = Column(Float)
    extracted_merchant = Column(String)
    extracted_date = Column(DateTime)
    
    # Fraud analysis
    is_forged = Column(Boolean, default=False)
    forgery_confidence = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    analysis_results = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MerchantNode(Base):
    """Merchant node for graph analysis"""
    __tablename__ = "merchant_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, unique=True, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    category = Column(String)
    location = Column(String)
    
    # Graph metrics
    centrality_score = Column(Float, default=0.0)
    clustering_coefficient = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    
    # Business metrics
    transaction_count = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    unique_customers = Column(Integer, default=0)
    
    # Fraud indicators
    flagged_transactions = Column(Integer, default=0)
    is_suspicious = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FlagEvent(Base):
    """Flag event for tracking fraud alerts"""
    __tablename__ = "flag_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, default=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    transaction_id = Column(String, index=True, nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False)  # anomaly, graph, receipt, spell
    severity = Column(String, default="medium")  # low, medium, high, critical
    confidence = Column(Float, nullable=False)
    
    # Analysis details
    triggered_by = Column(String)  # Which model/rule triggered
    factors = Column(JSON)  # Contributing factors
    explanation = Column(Text)
    
    # Status tracking
    status = Column(String, default="open")  # open, investigating, resolved, false_positive
    assigned_to = Column(String)  # Analyst assigned
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class SpellRun(Base):
    """Spell run for simulation tracking"""
    __tablename__ = "spell_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, default=lambda: f"SPELL-{uuid.uuid4().hex[:8].upper()}")
    
    # Spell details
    spell_name = Column(String, nullable=False)
    spell_type = Column(String, nullable=False)  # rug_pull, oracle_manipulation, etc.
    parameters = Column(JSON)  # Spell parameters
    
    # Execution details
    status = Column(String, default="running")  # running, completed, failed
    progress = Column(Float, default=0.0)
    
    # Results
    affected_transactions = Column(Integer, default=0)
    flagged_transactions = Column(Integer, default=0)
    total_impact = Column(Float, default=0.0)
    results = Column(JSON)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

class AlertConfig(Base):
    """Alert configuration for real-time notifications"""
    __tablename__ = "alert_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    # Thresholds
    fraud_score_threshold = Column(Float, default=0.7)
    amount_threshold = Column(Float, default=1000.0)
    graph_risk_threshold = Column(Float, default=0.8)
    
    # Notification settings
    email_enabled = Column(Boolean, default=True)
    websocket_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Recipients
    email_recipients = Column(JSON)
    phone_recipients = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)