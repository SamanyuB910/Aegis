from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from datetime import datetime

from models.pydantic_schemas import (
    ExplanationRequest, 
    ExplanationResponse
)
from services.anomaly_model import AnomalyDetector
from services.graph_model import MerchantGraphAnalyzer

router = APIRouter(prefix="/api/explain", tags=["AI Explanations"])
logger = logging.getLogger(__name__)

# Initialize AI explanation services
anomaly_detector = AnomalyDetector()
graph_analyzer = MerchantGraphAnalyzer()

@router.post("/transaction", response_model=ExplanationResponse)
async def explain_transaction(request: ExplanationRequest):
    """
    Generate AI explanation for why a transaction was flagged as fraudulent.
    
    Provides detailed analysis of:
    - Anomaly detection features
    - Risk scoring factors
    - Behavioral patterns
    - Merchant network analysis
    """
    try:
        logger.info(f"🔍 Generating transaction explanation for ID: {request.transaction_id}")
        
        # Get transaction data (in real implementation, fetch from database)
        transaction_data = await _get_transaction_data(request.transaction_id)
        
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Generate explanations
        explanations = []
        
        # Always include all types for now
        anomaly_explanation = await _explain_anomaly_detection(transaction_data)
        explanations.append(anomaly_explanation)
        
        risk_explanation = await _explain_risk_factors(transaction_data)
        explanations.append(risk_explanation)
        
        behavioral_explanation = await _explain_behavioral_patterns(transaction_data)
        explanations.append(behavioral_explanation)
        
        network_explanation = await _explain_network_analysis(transaction_data)
        explanations.append(network_explanation)
        
        # Generate overall summary
        summary = _generate_explanation_summary(transaction_data, explanations)
        
        response = ExplanationResponse(
            transaction_id=request.transaction_id,
            explanation_type="comprehensive",
            summary=summary,
            details=explanations,
            confidence_score=transaction_data.get("fraud_score", 0.0),
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Generated explanation for transaction {request.transaction_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating transaction explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.post("/merchant", response_model=ExplanationResponse)
async def explain_merchant_risk(merchant_id: str):
    """
    Generate AI explanation for merchant risk assessment.
    
    Analyzes:
    - Merchant transaction patterns
    - Network position and connections
    - Historical behavior trends
    - Risk indicators
    """
    try:
        logger.info(f"🔍 Generating merchant explanation for ID: {merchant_id}")
        
        # Get merchant data
        merchant_data = await _get_merchant_data(merchant_id)
        
        if not merchant_data:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        # Generate merchant-specific explanations
        explanations = []
        
        # Transaction pattern analysis
        pattern_explanation = await _explain_merchant_patterns(merchant_data)
        explanations.append(pattern_explanation)
        
        # Network analysis
        network_explanation = await _explain_merchant_network(merchant_data)
        explanations.append(network_explanation)
        
        # Risk trend analysis
        trend_explanation = await _explain_merchant_trends(merchant_data)
        explanations.append(trend_explanation)
        
        # Generate summary
        summary = f"Merchant {merchant_id} shows {merchant_data.get('risk_level', 'unknown')} risk level based on transaction patterns, network position, and historical behavior."
        
        response = ExplanationResponse(
            transaction_id=merchant_id,
            explanation_type="merchant_risk",
            summary=summary,
            details=explanations,
            confidence_score=merchant_data.get("risk_score", 0.0),
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Generated merchant explanation for {merchant_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating merchant explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.post("/pattern", response_model=ExplanationResponse)
async def explain_fraud_pattern(pattern_id: str):
    """
    Generate AI explanation for detected fraud patterns.
    
    Explains:
    - Pattern detection algorithms
    - Contributing factors
    - Similar historical cases
    - Recommended actions
    """
    try:
        logger.info(f"🔍 Generating pattern explanation for ID: {pattern_id}")
        
        # Get pattern data
        pattern_data = await _get_pattern_data(pattern_id)
        
        if not pattern_data:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        # Generate pattern explanations
        explanations = []
        
        # Algorithm explanation
        algorithm_explanation = await _explain_detection_algorithm(pattern_data)
        explanations.append(algorithm_explanation)
        
        # Contributing factors
        factors_explanation = await _explain_pattern_factors(pattern_data)
        explanations.append(factors_explanation)
        
        # Historical context
        historical_explanation = await _explain_historical_context(pattern_data)
        explanations.append(historical_explanation)
        
        # Recommendations
        recommendations_explanation = await _explain_recommendations(pattern_data)
        explanations.append(recommendations_explanation)
        
        # Generate summary
        summary = f"Pattern {pattern_id} detected using {pattern_data.get('algorithm', 'unknown')} algorithm with {pattern_data.get('confidence', 0.0):.1%} confidence."
        
        response = ExplanationResponse(
            transaction_id=pattern_id,
            explanation_type="fraud_pattern",
            summary=summary,
            details=explanations,
            confidence_score=pattern_data.get("confidence", 0.0),
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Generated pattern explanation for {pattern_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating pattern explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.get("/available-types")
async def get_available_explanation_types():
    """Get list of available explanation types"""
    return {
        "explanation_types": [
            {
                "type": "ANOMALY_FEATURES",
                "name": "Anomaly Detection Features",
                "description": "Explains which features contributed to anomaly detection"
            },
            {
                "type": "RISK_FACTORS", 
                "name": "Risk Scoring Factors",
                "description": "Breaks down risk score calculation and contributing factors"
            },
            {
                "type": "BEHAVIORAL_PATTERNS",
                "name": "Behavioral Pattern Analysis", 
                "description": "Analyzes user and merchant behavioral patterns"
            },
            {
                "type": "NETWORK_ANALYSIS",
                "name": "Network Graph Analysis",
                "description": "Shows network connections and graph-based insights"
            }
        ]
    }

# Helper functions for data retrieval (mock implementations)
async def _get_transaction_data(transaction_id: str) -> Dict[str, Any]:
    """Mock function to get transaction data - replace with actual database query"""
    # In real implementation, query database for transaction
    return {
        "transaction_id": transaction_id,
        "amount": 1250.00,
        "merchant_id": "MERCHANT_0042",
        "user_id": "USER_0123",
        "timestamp": datetime.utcnow(),
        "fraud_score": 0.87,
        "anomaly_features": {
            "amount_zscore": 2.3,
            "time_since_last": 45,
            "merchant_risk": 0.65,
            "velocity_1h": 3,
            "unusual_time": True
        },
        "risk_factors": {
            "high_amount": True,
            "new_merchant": False,
            "off_hours": True,
            "multiple_recent": True,
            "geo_anomaly": False
        }
    }

async def _get_merchant_data(merchant_id: str) -> Dict[str, Any]:
    """Mock function to get merchant data"""
    return {
        "merchant_id": merchant_id,
        "name": f"Merchant {merchant_id}",
        "risk_score": 0.72,
        "risk_level": "high",
        "transaction_count": 1250,
        "total_volume": 125000.50,
        "network_metrics": {
            "centrality": 0.45,
            "clustering": 0.23,
            "community": "high_risk_cluster"
        }
    }

async def _get_pattern_data(pattern_id: str) -> Dict[str, Any]:
    """Mock function to get pattern data"""
    return {
        "pattern_id": pattern_id,
        "pattern_type": "rug_pull",
        "algorithm": "graph_clustering",
        "confidence": 0.89,
        "affected_merchants": 3,
        "affected_users": 45,
        "total_impact": 25000.00
    }

# Explanation generation functions
async def _explain_anomaly_detection(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for anomaly detection results"""
    features = transaction_data.get("anomaly_features", {})
    
    explanations = []
    
    if features.get("amount_zscore", 0) > 2.0:
        explanations.append("Transaction amount is significantly higher than typical for this user (2.3 standard deviations above normal)")
    
    if features.get("unusual_time"):
        explanations.append("Transaction occurred at an unusual time (outside normal business hours)")
    
    if features.get("velocity_1h", 0) > 2:
        explanations.append(f"High transaction velocity: {features['velocity_1h']} transactions in the past hour")
    
    if features.get("merchant_risk", 0) > 0.5:
        explanations.append(f"Merchant has elevated risk score: {features['merchant_risk']:.2f}")
    
    return {
        "category": "Anomaly Detection",
        "title": "Statistical Anomaly Analysis",
        "explanations": explanations,
        "technical_details": features,
        "impact_score": min(len(explanations) * 0.2, 1.0)
    }

async def _explain_risk_factors(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for risk factors"""
    risk_factors = transaction_data.get("risk_factors", {})
    
    explanations = []
    active_factors = []
    
    for factor, is_active in risk_factors.items():
        if is_active:
            active_factors.append(factor)
            
            if factor == "high_amount":
                explanations.append("Transaction amount exceeds user's typical spending pattern")
            elif factor == "new_merchant":
                explanations.append("First-time transaction with this merchant")
            elif factor == "off_hours":
                explanations.append("Transaction occurred outside normal business hours")
            elif factor == "multiple_recent":
                explanations.append("Multiple transactions in short time period")
            elif factor == "geo_anomaly":
                explanations.append("Transaction location differs from user's normal patterns")
    
    return {
        "category": "Risk Assessment",
        "title": "Risk Factor Analysis", 
        "explanations": explanations,
        "active_factors": active_factors,
        "risk_score_contribution": len(active_factors) * 0.15
    }

async def _explain_behavioral_patterns(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for behavioral patterns"""
    return {
        "category": "Behavioral Analysis",
        "title": "User & Merchant Behavior Patterns",
        "explanations": [
            "User's spending pattern shows significant deviation from historical norms",
            "Transaction timing aligns with known fraud attack patterns",
            "Merchant interaction pattern suggests coordinated activity"
        ],
        "pattern_matches": ["unusual_spending", "time_clustering", "coordination_signals"],
        "confidence": 0.78
    }

async def _explain_network_analysis(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for network analysis"""
    return {
        "category": "Network Analysis",
        "title": "Merchant Network Position & Connections",
        "explanations": [
            "Merchant shows high centrality in suspicious transaction network",
            "Connected to multiple flagged merchants through shared customers",
            "Part of identified high-risk merchant cluster"
        ],
        "network_metrics": {
            "centrality_score": 0.67,
            "cluster_risk": 0.89,
            "connection_count": 23
        }
    }

async def _explain_merchant_patterns(merchant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate merchant pattern explanation"""
    return {
        "category": "Merchant Patterns",
        "title": "Transaction Pattern Analysis",
        "explanations": [
            f"Processed {merchant_data['transaction_count']} transactions with total volume ${merchant_data['total_volume']:,.2f}",
            "Shows unusual spike in transaction volume over past 24 hours",
            "Transaction amounts cluster around specific values suggesting automation"
        ]
    }

async def _explain_merchant_network(merchant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate merchant network explanation"""
    metrics = merchant_data.get("network_metrics", {})
    return {
        "category": "Network Position",
        "title": "Merchant Network Analysis",
        "explanations": [
            f"High centrality score ({metrics.get('centrality', 0):.2f}) indicates central position in transaction network",
            f"Belongs to {metrics.get('community', 'unknown')} community cluster",
            "Connected to multiple high-risk merchants through shared transaction patterns"
        ]
    }

async def _explain_merchant_trends(merchant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate merchant trend explanation"""
    return {
        "category": "Risk Trends", 
        "title": "Historical Risk Trend Analysis",
        "explanations": [
            "Risk score has increased 45% over past 30 days",
            "Transaction velocity shows concerning upward trend",
            "Customer complaint rate above industry average"
        ]
    }

async def _explain_detection_algorithm(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate algorithm explanation"""
    return {
        "category": "Detection Algorithm",
        "title": f"Pattern Detection: {pattern_data.get('algorithm', 'Unknown')}",
        "explanations": [
            "Graph clustering algorithm identified coordinated merchant activity",
            "Statistical analysis detected anomalous transaction patterns",
            "Machine learning model flagged behavioral inconsistencies"
        ]
    }

async def _explain_pattern_factors(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate pattern factors explanation"""
    return {
        "category": "Contributing Factors",
        "title": "Key Pattern Indicators",
        "explanations": [
            f"Affected {pattern_data.get('affected_merchants', 0)} merchants and {pattern_data.get('affected_users', 0)} users",
            f"Total financial impact: ${pattern_data.get('total_impact', 0):,.2f}",
            "Coordinated timing suggests organized fraud operation"
        ]
    }

async def _explain_historical_context(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate historical context explanation"""
    return {
        "category": "Historical Context",
        "title": "Similar Past Incidents",
        "explanations": [
            "Similar pattern detected 3 times in past 6 months",
            "Previous incidents resulted in average loss of $15,000",
            "Pattern typically escalates over 7-14 day period"
        ]
    }

async def _explain_recommendations(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendations explanation"""
    return {
        "category": "Recommendations",
        "title": "Suggested Actions",
        "explanations": [
            "Immediate: Flag all transactions from affected merchants",
            "Short-term: Enhanced monitoring of related accounts",
            "Long-term: Update detection rules based on pattern characteristics"
        ]
    }

def _generate_explanation_summary(transaction_data: Dict[str, Any], explanations: List[Dict[str, Any]]) -> str:
    """Generate overall explanation summary"""
    fraud_score = transaction_data.get("fraud_score", 0.0)
    amount = transaction_data.get("amount", 0.0)
    
    risk_level = "HIGH" if fraud_score > 0.8 else "MEDIUM" if fraud_score > 0.5 else "LOW"
    
    summary = f"Transaction flagged as {risk_level} RISK (score: {fraud_score:.2f}) for ${amount:,.2f}. "
    
    key_factors = len([exp for exp in explanations if exp.get("impact_score", 0) > 0.5])
    
    summary += f"Analysis identified {key_factors} critical risk factors across anomaly detection, "
    summary += "behavioral patterns, and network analysis. "
    
    if fraud_score > 0.8:
        summary += "Immediate review recommended due to high fraud likelihood."
    elif fraud_score > 0.5:
        summary += "Enhanced monitoring suggested due to elevated risk signals."
    else:
        summary += "Transaction appears normal but flagged due to precautionary measures."
    
    return summary