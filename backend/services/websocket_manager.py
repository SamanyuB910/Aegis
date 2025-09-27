from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    WebSocket manager for real-time fraud alerts and notifications
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.alert_queue: List[Dict[str, Any]] = []
        self.is_running = False
        
    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to FraudX+ real-time alerts",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert to all connected clients"""
        if not self.active_connections:
            logger.info("📢 No active connections for alert broadcast")
            return
        
        message = {
            "type": "fraud_alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
                logger.info(f"📢 Alert broadcasted to client: {alert_data.get('transaction_id', 'unknown')}")
            except Exception as e:
                logger.error(f"❌ Failed to send alert to client: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
    
    async def broadcast_metrics_update(self, metrics: Dict[str, Any]):
        """Broadcast metrics update to all connected clients"""
        message = {
            "type": "metrics_update",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_all(message)
    
    async def broadcast_transaction_update(self, transaction: Dict[str, Any]):
        """Broadcast new transaction to all connected clients"""
        message = {
            "type": "transaction_update",
            "data": transaction,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_all(message)
    
    async def broadcast_spell_result(self, spell_result: Dict[str, Any]):
        """Broadcast spell simulation result to all connected clients"""
        message = {
            "type": "spell_result",
            "data": spell_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_all(message)
    
    async def _broadcast_to_all(self, message: Dict[str, Any]):
        """Internal method to broadcast message to all connections"""
        if not self.active_connections:
            return
        
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Failed to broadcast message: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
    
    async def start_alert_simulator(self):
        """Start background alert simulator for demo purposes"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🎯 Starting alert simulator...")
        
        while self.is_running:
            try:
                # Wait between 30-120 seconds for next simulated alert
                await asyncio.sleep(random.randint(30, 120))
                
                if self.active_connections:
                    # Generate random alert
                    alert = self._generate_random_alert()
                    await self.broadcast_alert(alert)
                
            except Exception as e:
                logger.error(f"❌ Alert simulator error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    def _generate_random_alert(self) -> Dict[str, Any]:
        """Generate random fraud alert for simulation"""
        alert_types = [
            {
                "severity": "critical",
                "title": "Unusual spending pattern detected",
                "reasons": ["High velocity transactions", "Unusual merchant category", "Off-hours activity"]
            },
            {
                "severity": "high", 
                "title": "Receipt-transaction mismatch",
                "reasons": ["OCR discrepancy", "Amount mismatch", "Merchant name mismatch"]
            },
            {
                "severity": "high",
                "title": "Merchant network anomaly",
                "reasons": ["Suspicious merchant cluster", "High centrality score", "Collusion pattern"]
            },
            {
                "severity": "medium",
                "title": "Voice stress indicators",
                "reasons": ["Elevated stress markers", "Unusual speech patterns", "Authentication concerns"]
            },
            {
                "severity": "high",
                "title": "Geographic anomaly",
                "reasons": ["Impossible travel time", "High-risk location", "VPN usage detected"]
            }
        ]
        
        merchants = [
            "QuickMart #247", "TechStore Online", "FuelStop #89", "Restaurant Plaza",
            "Electronics Hub", "Fashion Outlet", "Coffee Express", "Auto Parts Direct",
            "Grocery Central", "Sports Equipment Co"
        ]
        
        amounts = [
            "$127.45", "$899.99", "$67.23", "$45.67", "$1,234.56", "$2,847.50",
            "$89.45", "$299.99", "$156.78", "$3,456.78"
        ]
        
        # Select random alert type
        alert_type = random.choice(alert_types)
        
        return {
            "transaction_id": f"TXN-{random.randint(10000, 99999)}",
            "severity": alert_type["severity"],
            "title": alert_type["title"],
            "merchant": random.choice(merchants),
            "amount": random.choice(amounts),
            "confidence": round(random.uniform(0.7, 0.98), 2),
            "factors": random.sample(alert_type["reasons"], random.randint(1, len(alert_type["reasons"]))),
            "time": f"{random.randint(1, 30)} min ago",
            "location": random.choice(["New York, NY", "Los Angeles, CA", "Chicago, IL", "Miami, FL", "Online"])
        }
    
    def stop_alert_simulator(self):
        """Stop the alert simulator"""
        self.is_running = False
        logger.info("🛑 Alert simulator stopped")
    
    async def send_system_notification(self, notification: Dict[str, Any]):
        """Send system notification to all connected clients"""
        message = {
            "type": "system_notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_all(message)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "alert_queue_size": len(self.alert_queue),
            "simulator_running": self.is_running,
            "uptime": "Active"  # Could track actual uptime
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()