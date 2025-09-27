from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CLEARED = "cleared"
    FLAGGED = "flagged"
    REVIEWING = "reviewing"

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class SpellType(str, Enum):
    RUG_PULL = "rug_pull"
    ORACLE_MANIPULATION = "oracle_manipulation"
    SYBIL_ATTACK = "sybil_attack"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    MERCHANT_COLLUSION = "merchant_collusion"

# Transaction Schemas
class TransactionBase(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant_id: str = Field(..., description="Merchant identifier")
    merchant_name: str = Field(..., description="Merchant display name")
    category: Optional[str] = Field(None, description="Transaction category")
    location: Optional[str] = Field(None, description="Transaction location")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TransactionCreate(TransactionBase):
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TransactionResponse(TransactionBase):
    id: int
    txn_id: str
    timestamp: datetime
    fraud_score: float = Field(description="ML fraud score (0-1)")
    graph_risk_score: float = Field(description="Graph analysis risk score (0-1)")
    is_flagged: bool
    status: TransactionStatus
    anomaly_factors: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Fraud Analysis Schemas
class FraudScoreResponse(BaseModel):
    transaction_id: str
    fraud_score: float = Field(description="Overall fraud probability (0-1)")
    graph_risk_score: float = Field(description="Graph-based risk score (0-1)")
    is_flagged: bool
    factors: List[str] = Field(description="Contributing risk factors")
    confidence: float = Field(description="Model confidence (0-1)")
    timestamp: datetime

class AnomalyFactors(BaseModel):
    isolation_forest_score: float
    local_outlier_factor: float
    amount_zscore: float
    velocity_score: float
    merchant_risk: float
    time_risk: float

# Receipt Schemas
class ReceiptBase(BaseModel):
    transaction_id: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    filename: str
    content_type: str

class ReceiptResponse(ReceiptBase):
    id: int
    receipt_id: str
    filename: str
    file_path: str
    file_size: int
    content_type: str
    ocr_text: Optional[str] = None
    extracted_amount: Optional[float] = None
    extracted_merchant: Optional[str] = None
    extracted_date: Optional[datetime] = None
    is_forged: bool
    forgery_confidence: float
    anomaly_score: float
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class OCRResult(BaseModel):
    text: str
    confidence: float
    extracted_fields: Dict[str, Any]
    anomalies: List[str]

class ForgeryAnalysis(BaseModel):
    is_forged: bool
    confidence: float
    reasons: List[str]
    technical_details: Dict[str, Any]

# Spell Simulation Schemas
class SpellContext(BaseModel):
    target_merchants: Optional[List[str]] = None
    target_users: Optional[List[str]] = None
    time_window_hours: int = Field(default=24, ge=1, le=168)
    severity_level: float = Field(default=0.8, ge=0.1, le=1.0)

class SpellRequest(BaseModel):
    spell_name: SpellType
    context: SpellContext
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SpellResult(BaseModel):
    run_id: str
    spell_name: str
    status: str
    progress: float
    affected_transactions: int
    flagged_transactions: int
    total_impact: float
    results: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

# Explanation Schemas
class ExplanationRequest(BaseModel):
    transaction_id: str
    include_technical: bool = Field(default=False, description="Include technical ML details")

class ExplanationResponse(BaseModel):
    transaction_id: str
    explanation_type: str
    summary: str = Field(description="Human-readable summary")
    details: List[Dict[str, Any]] = Field(description="Detailed explanations")
    confidence_score: float = Field(description="Overall confidence (0-1)")
    generated_at: datetime

# Graph Analysis Schemas
class MerchantRiskResponse(BaseModel):
    merchant_id: str
    risk_score: float
    centrality_score: float
    clustering_coefficient: float
    connected_merchants: List[str]
    suspicious_patterns: List[str]
    recommendations: List[str]

class GraphMetrics(BaseModel):
    total_nodes: int
    total_edges: int
    avg_clustering: float
    diameter: int
    suspicious_clusters: int

# Alert Schemas
class AlertBase(BaseModel):
    severity: SeverityLevel
    title: str
    message: str
    
class FraudAlert(AlertBase):
    transaction_id: str
    merchant: str
    amount: str
    confidence: float
    factors: List[str]

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# User Schemas
class UserBase(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    risk_profile: str
    account_age_days: int
    historical_fraud_score: float
    transaction_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardMetrics(BaseModel):
    total_transactions: str
    fraud_cases_detected: str
    money_saved: str
    false_positive_rate: str
    fraud_rate: float
    trend_data: List[Dict[str, Any]]

class LiveAlert(BaseModel):
    id: int
    severity: str
    title: str
    merchant: str
    amount: str
    time: str
    confidence: float

class TransactionFeedItem(BaseModel):
    id: str
    bank: str
    merchant: str
    amount: str
    location: str
    status: str
    time: str

# API Response Wrappers
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int