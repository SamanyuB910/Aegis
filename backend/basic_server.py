"""
FraudX+ Copilot - Basic HTTP Server (No FastAPI)
A minimal HTTP server for the fraud detection API using only Python standard library.
"""

import http.server
import socketserver
import json
import sqlite3
from datetime import datetime
import random
from urllib.parse import urlparse, parse_qs
import os

class FraudAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/' or path == '/api':
                response = {
                    "message": "FraudX+ Copilot API - Basic Version",
                    "version": "1.0.0",
                    "status": "running",
                    "endpoints": {
                        "health": "/api/health",
                        "dashboard": "/api/analytics/dashboard",
                        "transactions": "/api/transactions"
                    }
                }
            
            elif path == '/api/health':
                response = self.get_health()
            
            elif path == '/api/analytics/dashboard':
                response = self.get_dashboard_data()
            
            elif path == '/api/transactions':
                response = self.get_transactions()
            
            elif path == '/api/spells/types':
                response = self.get_spell_types()
            
            else:
                response = {"error": "Endpoint not found", "path": path}
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/api/spells/execute':
                response = self.execute_spell()
            else:
                response = {"error": "POST endpoint not found", "path": path}
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect("fraudx_copilot.db")
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_health(self):
        """Health check endpoint"""
        conn = self.get_db_connection()
        db_status = "connected" if conn else "disconnected"
        if conn:
            conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "server": "Python HTTP Server"
        }
    
    def get_dashboard_data(self):
        """Get dashboard analytics data"""
        conn = self.get_db_connection()
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
    
    def get_transactions(self):
        """Get transactions"""
        conn = self.get_db_connection()
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
    
    def execute_spell(self):
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
            "status": "completed",
            "message": "Spell execution simulated successfully"
        }
    
    def get_spell_types(self):
        """Get available spell types"""
        return {
            "success": True,
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

def start_server():
    """Start the HTTP server"""
    PORT = 8000
    
    print(f"🚀 Starting FraudX+ Copilot API Server...")
    print(f"📍 Server running at: http://localhost:{PORT}")
    print(f"🔗 API Documentation: http://localhost:{PORT}/")
    print(f"💾 Database: fraudx_copilot.db")
    print(f"🌐 CORS enabled for frontend at localhost:3001")
    print(f"⚡ Endpoints available:")
    print(f"   GET  /api/health")
    print(f"   GET  /api/analytics/dashboard")
    print(f"   GET  /api/transactions")
    print(f"   GET  /api/spells/types")
    print(f"   POST /api/spells/execute")
    print(f"\n✨ Server ready! You can now connect the frontend.")
    
    try:
        with socketserver.TCPServer(("", PORT), FraudAPIHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    start_server()