"""
FraudX+ Copilot - Ultra Simple FastAPI Backend MVP
A basic version of the fraud detection API using only essential dependencies.
"""

from fastapi import FastAPI
import json
import sqlite3
from datetime import datetime
import random

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="FraudX+ Copilot API",
    description="AI-Powered Fraud Detection System - Simple Version", 
    version="1.0.0"
)

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect("fraudx_copilot.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FraudX+ Copilot API - Simple Version",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "dashboard": "/api/analytics/dashboard", 
            "transactions": "/api/transactions"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    if conn:
        conn.close()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }

@app.get("/api/analytics/dashboard")
async def get_dashboard_data():
    """Get dashboard analytics data"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        cursor = conn.cursor()
        
        # Get transaction stats
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as flagged FROM transactions WHERE is_flagged = 1")
        flagged_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(fraud_score) as avg_score FROM transactions")
        avg_fraud_score_result = cursor.fetchone()[0]
        avg_fraud_score = avg_fraud_score_result if avg_fraud_score_result else 0
        
        cursor.execute("SELECT SUM(amount) as total FROM transactions")
        total_volume_result = cursor.fetchone()[0]
        total_volume = total_volume_result if total_volume_result else 0
        
        # Get recent transactions
        cursor.execute("""
            SELECT t.id, t.user_id, t.merchant_id, t.amount, t.fraud_score, t.is_flagged, t.timestamp,
                   u.full_name as user_name, m.name as merchant_name 
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN merchants m ON t.merchant_id = m.id
            ORDER BY t.timestamp DESC LIMIT 10
        """)
        
        recent_transactions = []
        for row in cursor.fetchall():
            recent_transactions.append({
                "id": row[0],
                "user_id": row[1], 
                "merchant_id": row[2],
                "amount": row[3],
                "fraud_score": row[4],
                "is_flagged": bool(row[5]),
                "timestamp": row[6],
                "user_name": row[7],
                "merchant_name": row[8]
            })
        
        conn.close()
        
        return {
            "success": True,
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
        
    except Exception as e:
        if conn:
            conn.close()
        return {"error": f"Database query failed: {str(e)}"}

@app.get("/api/transactions")
async def get_transactions():
    """Get transactions"""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.user_id, t.merchant_id, t.amount, t.fraud_score, t.is_flagged, t.timestamp,
                   u.full_name as user_name, m.name as merchant_name 
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN merchants m ON t.merchant_id = m.id
            ORDER BY t.timestamp DESC LIMIT 50
        """)
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                "id": row[0],
                "user_id": row[1],
                "merchant_id": row[2], 
                "amount": row[3],
                "fraud_score": row[4],
                "is_flagged": bool(row[5]),
                "timestamp": row[6],
                "user_name": row[7],
                "merchant_name": row[8]
            })
        
        conn.close()
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        if conn:
            conn.close()
        return {"error": f"Database query failed: {str(e)}"}

@app.post("/api/spells/execute")
async def execute_spell():
    """Execute a fraud simulation spell"""
    return {
        "success": True,
        "spell_type": "rug_pull",
        "execution_id": f"SPELL_{random.randint(1000, 9999)}",
        "started_at": datetime.utcnow().isoformat(),
        "affected_transactions": random.randint(20, 80),
        "flagged_transactions": random.randint(15, 65),
        "total_impact": round(random.uniform(5000, 25000), 2),
        "detection_rate": round(random.uniform(0.75, 0.95), 3),
        "status": "completed"
    }

@app.get("/api/spells/types")
async def get_spell_types():
    """Get available spell types"""
    return {
        "success": True,
        "spell_types": [
            {
                "type": "rug_pull",
                "name": "Rug Pull Attack",
                "description": "Simulates merchant disappearing with funds"
            },
            {
                "type": "oracle_manipulation", 
                "name": "Oracle Manipulation",
                "description": "Price feed manipulation scenarios"
            },
            {
                "type": "sybil_attack",
                "name": "Sybil Attack", 
                "description": "Coordinated multiple fake account attacks"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)