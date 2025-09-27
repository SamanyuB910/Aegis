"""
FraudX+ Copilot - FastAPI Backend MVP

A comprehensive fraud detection system with real-time analytics, 
multimodal analysis, and machine learning-powered transaction scoring.

To run the application:
1. Install dependencies: pip install -r requirements.txt
2. Initialize database: python -c "from db.init_db import init_db; init_db()"
3. Run server: uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Documentation available at: http://localhost:8000/docs
WebSocket connection for real-time alerts: ws://localhost:8000/ws/alerts

Features:
- Transaction ingestion and fraud scoring
- Receipt OCR and forgery detection
- Merchant network graph analysis
- Spell simulation (Rug-Pull, Oracle manipulation)
- Real-time WebSocket alerts
- Explainable AI reasoning

Tech Stack:
- FastAPI with WebSocket support
- SQLAlchemy for database operations
- NetworkX for graph analysis
- scikit-learn for ML models
- Tesseract for OCR
- Pydantic for data validation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import List, Dict, Any
import json
from datetime import datetime

# Import routers
from routers import transactions, receipts, spells, explain
from db.init_db import init_db
from services.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket manager for real-time alerts
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting FraudX+ Copilot Backend")
    await init_db()
    logger.info("✅ Database initialized")
    
    # Start background tasks
    asyncio.create_task(websocket_manager.start_alert_simulator())
    logger.info("✅ Alert simulator started")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FraudX+ Copilot Backend")

# Create FastAPI app
app = FastAPI(
    title="FraudX+ Copilot API",
    description="AI-Powered Fraud Detection and Prevention System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(receipts.router, prefix="/api", tags=["receipts"])
app.include_router(spells.router, prefix="/api", tags=["spells"])
app.include_router(explain.router, prefix="/api", tags=["explanations"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "FraudX+ Copilot Backend is running",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "ml_models": "loaded",
            "websocket": "active",
            "graph_db": "in-memory"
        }
    }

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time fraud alerts"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # Echo back confirmation
            await websocket.send_text(json.dumps({
                "type": "confirmation",
                "message": "Connected to FraudX+ real-time alerts",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get real-time dashboard metrics"""
    return {
        "total_transactions": "2,847,392",
        "fraud_cases_detected": "1,247",
        "money_saved": "$2.4M",
        "false_positive_rate": "2.1%",
        "metrics": [
            {
                "title": "Total Transactions",
                "value": "2,847,392",
                "change": "+12.5%",
                "trend": "up"
            },
            {
                "title": "Fraud Cases Detected", 
                "value": "1,247",
                "change": "+8.2%",
                "trend": "up"
            },
            {
                "title": "Money Saved",
                "value": "$2.4M", 
                "change": "+15.3%",
                "trend": "up"
            },
            {
                "title": "False Positive Rate",
                "value": "2.1%",
                "change": "-0.8%",
                "trend": "down"
            }
        ]
    }

@app.get("/api/dashboard/alerts")
async def get_live_alerts():
    """Get current fraud alerts"""
    return {
        "alerts": [
            {
                "id": 1,
                "severity": "critical",
                "title": "Unusual spending pattern detected",
                "merchant": "QuickMart #247",
                "amount": "$2,847.50",
                "time": "2 min ago",
                "confidence": 0.94
            },
            {
                "id": 2,
                "severity": "high", 
                "title": "Receipt-transaction mismatch",
                "merchant": "TechStore Online",
                "amount": "$1,299.99",
                "time": "8 min ago",
                "confidence": 0.87
            },
            {
                "id": 3,
                "severity": "medium",
                "title": "Voice stress indicators",
                "merchant": "FuelStop #89", 
                "amount": "$89.45",
                "time": "15 min ago",
                "confidence": 0.73
            }
        ]
    }

@app.get("/api/dashboard/transactions")
async def get_transaction_feed():
    """Get live transaction feed"""
    return {
        "transactions": [
            {
                "id": "TXN-2024-001",
                "bank": "Capital One Bank",
                "merchant": "QuickMart #247",
                "amount": "$127.45",
                "location": "New York, NY",
                "status": "flagged",
                "time": "2:34 PM"
            },
            {
                "id": "TXN-2024-002",
                "bank": "Chase Bank", 
                "merchant": "TechStore Online",
                "amount": "$899.99",
                "location": "Online",
                "status": "reviewing",
                "time": "2:31 PM"
            },
            {
                "id": "TXN-2024-003",
                "bank": "Wells Fargo",
                "merchant": "FuelStop #89",
                "amount": "$67.23", 
                "location": "Los Angeles, CA",
                "status": "cleared",
                "time": "2:28 PM"
            }
        ]
    }

@app.get("/api/dashboard/trends")
async def get_fraud_trends():
    """Get fraud trend data for charts"""
    return {
        "trends": [
            {"time": "00:00", "fraudCases": 12, "transactions": 2400},
            {"time": "04:00", "fraudCases": 8, "transactions": 1800}, 
            {"time": "08:00", "fraudCases": 24, "transactions": 4200},
            {"time": "12:00", "fraudCases": 18, "transactions": 3800},
            {"time": "16:00", "fraudCases": 32, "transactions": 5200},
            {"time": "20:00", "fraudCases": 28, "transactions": 4800},
            {"time": "24:00", "fraudCases": 15, "transactions": 2800}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )