"""
FraudX+ Copilot - Simplified FastAPI Backend MVP
A minimal version of the fraud detection API that works with basic dependencies.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import sqlite3
from datetime import datetime
import random

app = FastAPI(
    title="FraudX+ Copilot API",
    description="AI-Powered Fraud Detection System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect("fraudx_copilot.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FraudX+ Copilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }

@app.get("/api/analytics/dashboard")
async def get_dashboard_data():
    """Get dashboard analytics data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get transaction stats
    cursor.execute("SELECT COUNT(*) as total FROM transactions")
    total_transactions = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as flagged FROM transactions WHERE is_flagged = 1")
    flagged_transactions = cursor.fetchone()["flagged"]
    
    cursor.execute("SELECT AVG(fraud_score) as avg_score FROM transactions")
    avg_fraud_score = cursor.fetchone()["avg_score"] or 0
    
    cursor.execute("SELECT SUM(amount) as total FROM transactions")
    total_volume = cursor.fetchone()["total"] or 0
    
    # Get recent transactions
    cursor.execute("""
        SELECT t.*, u.full_name as user_name, m.name as merchant_name 
        FROM transactions t
        LEFT JOIN users u ON t.user_id = u.id
        LEFT JOIN merchants m ON t.merchant_id = m.id
        ORDER BY t.timestamp DESC LIMIT 10
    """)
    recent_transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "metrics": {
            "total_transactions": total_transactions,
            "flagged_transactions": flagged_transactions,
            "fraud_detection_rate": round((flagged_transactions / total_transactions * 100) if total_transactions > 0 else 0, 2),
            "average_fraud_score": round(avg_fraud_score, 3),
            "total_volume": round(total_volume, 2),
            "active_alerts": flagged_transactions
        },
        "recent_transactions": recent_transactions,
        "fraud_trend": [
            {"date": "2024-01-01", "fraud_count": random.randint(5, 15)},
            {"date": "2024-01-02", "fraud_count": random.randint(8, 20)},
            {"date": "2024-01-03", "fraud_count": random.randint(3, 12)},
            {"date": "2024-01-04", "fraud_count": random.randint(6, 18)},
            {"date": "2024-01-05", "fraud_count": random.randint(9, 22)},
            {"date": "2024-01-06", "fraud_count": random.randint(4, 14)},
            {"date": "2024-01-07", "fraud_count": random.randint(7, 19)}
        ]
    }

@app.get("/api/transactions")
async def get_transactions(limit: int = 50, flagged_only: bool = False):
    """Get transactions with optional filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT t.*, u.full_name as user_name, m.name as merchant_name 
        FROM transactions t
        LEFT JOIN users u ON t.user_id = u.id
        LEFT JOIN merchants m ON t.merchant_id = m.id
    """
    
    if flagged_only:
        query += " WHERE t.is_flagged = 1"
    
    query += f" ORDER BY t.timestamp DESC LIMIT {limit}"
    
    cursor.execute(query)
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "transactions": transactions,
        "count": len(transactions)
    }

@app.post("/api/spells/execute")
async def execute_spell(spell_data: dict):
    """Execute a fraud simulation spell"""
    spell_type = spell_data.get("spell_type", "rug_pull")
    
    # Simulate spell execution
    simulation_result = {
        "success": True,
        "spell_type": spell_type,
        "execution_id": f"SPELL_{random.randint(1000, 9999)}",
        "started_at": datetime.utcnow().isoformat(),
        "affected_transactions": random.randint(20, 80),
        "flagged_transactions": random.randint(15, 65),
        "total_impact": round(random.uniform(5000, 25000), 2),
        "detection_rate": round(random.uniform(0.75, 0.95), 3),
        "status": "completed"
    }
    
    return simulation_result

@app.get("/api/spells/types")
async def get_spell_types():
    """Get available spell types"""
    return {
        "spell_types": [
            {
                "type": "rug_pull",
                "name": "Rug Pull Attack",
                "description": "Simulates merchant disappearing with funds",
                "duration": "5-10 minutes",
                "complexity": "medium"
            },
            {
                "type": "oracle_manipulation",
                "name": "Oracle Manipulation",
                "description": "Price feed manipulation scenarios",
                "duration": "10-15 minutes", 
                "complexity": "high"
            },
            {
                "type": "sybil_attack",
                "name": "Sybil Attack",
                "description": "Coordinated multiple fake account attacks",
                "duration": "15-20 minutes",
                "complexity": "high"
            },
            {
                "type": "flash_loan_attack",
                "name": "Flash Loan Attack",
                "description": "DeFi protocol exploitation simulation",
                "duration": "3-5 minutes",
                "complexity": "critical"
            },
            {
                "type": "merchant_collusion",
                "name": "Merchant Collusion",
                "description": "Coordinated merchant fraud networks",
                "duration": "20-30 minutes",
                "complexity": "high"
            }
        ]
    }

@app.post("/api/transactions/{transaction_id}/review")
async def review_transaction(transaction_id: str, review_data: dict):
    """Review a flagged transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update transaction review status
    cursor.execute("""
        UPDATE transactions 
        SET reviewed = 1, review_notes = ?
        WHERE id = ?
    """, (review_data.get("notes", ""), transaction_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "reviewed": True,
        "reviewer": "system",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/merchants/{merchant_id}/risk")
async def get_merchant_risk(merchant_id: str):
    """Get merchant risk analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM merchants WHERE id = ?", (merchant_id,))
    merchant = cursor.fetchone()
    
    if not merchant:
        return {"error": "Merchant not found"}
    
    cursor.execute("""
        SELECT COUNT(*) as transaction_count, 
               SUM(amount) as total_volume,
               AVG(fraud_score) as avg_fraud_score,
               COUNT(CASE WHEN is_flagged = 1 THEN 1 END) as flagged_count
        FROM transactions WHERE merchant_id = ?
    """, (merchant_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        "merchant": dict(merchant),
        "transaction_stats": dict(stats),
        "risk_analysis": {
            "risk_level": "high" if merchant["risk_score"] > 0.7 else "medium" if merchant["risk_score"] > 0.4 else "low",
            "network_position": "central" if random.random() > 0.5 else "peripheral",
            "behavioral_score": round(random.uniform(0.3, 0.9), 3),
            "reputation_score": round(random.uniform(0.6, 1.0), 3)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)