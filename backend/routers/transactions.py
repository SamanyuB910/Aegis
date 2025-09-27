from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from models.pydantic_schemas import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionUpdate,
    FraudScoreResponse
)
from models.db_models import Transaction, get_db
from services.anomaly_model import AnomalyDetector
from services.graph_model import MerchantGraphAnalyzer
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize ML services
anomaly_detector = AnomalyDetector()
graph_analyzer = MerchantGraphAnalyzer()

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ingest a new transaction and perform fraud detection analysis
    """
    try:
        # Create transaction record
        db_transaction = Transaction(
            user_id=transaction.user_id,
            amount=transaction.amount,
            merchant_id=transaction.merchant_id,
            merchant_name=transaction.merchant_name,
            category=transaction.category,
            location=transaction.location,
            timestamp=transaction.timestamp or datetime.utcnow(),
            transaction_metadata=transaction.metadata or {}
        )
        
        # Calculate fraud score using ML model
        fraud_score = await anomaly_detector.score_transaction(transaction)
        db_transaction.fraud_score = fraud_score
        
        # Update merchant graph
        graph_risk = await graph_analyzer.analyze_merchant_risk(
            transaction.merchant_id, 
            transaction.user_id
        )
        db_transaction.graph_risk_score = graph_risk.get("risk_score", 0.0)
        
        # Determine if transaction is flagged
        is_flagged = fraud_score > 0.7 or graph_risk.get("risk_score", 0) > 0.8
        db_transaction.is_flagged = is_flagged
        db_transaction.status = "flagged" if is_flagged else "cleared"
        
        # Save to database
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        logger.info(f"Transaction {db_transaction.txn_id} processed with fraud score: {fraud_score}")
        
        # Send real-time alert if flagged
        if is_flagged:
            alert_data = {
                "type": "fraud_alert",
                "transaction_id": db_transaction.txn_id,
                "merchant": transaction.merchant_name,
                "amount": f"${transaction.amount:,.2f}",
                "fraud_score": fraud_score,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "critical" if fraud_score > 0.9 else "high"
            }
            background_tasks.add_task(websocket_manager.broadcast_alert, alert_data)
        
        return TransactionResponse.from_orm(db_transaction)
        
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction processing failed: {str(e)}")

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    flagged_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve recent transactions with fraud scores and flags
    """
    try:
        query = db.query(Transaction)
        
        if flagged_only:
            query = query.filter(Transaction.is_flagged == True)
            
        transactions = query.order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()
        
        return [TransactionResponse.from_orm(txn) for txn in transactions]
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transactions")

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """
    Get a specific transaction by ID
    """
    transaction = db.query(Transaction).filter(Transaction.txn_id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    return TransactionResponse.from_orm(transaction)

@router.post("/transactions/{transaction_id}/rescore", response_model=FraudScoreResponse)
async def rescore_transaction(
    transaction_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recalculate fraud score for an existing transaction
    """
    transaction = db.query(Transaction).filter(Transaction.txn_id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    try:
        # Create transaction data for rescoring
        txn_data = TransactionCreate(
            user_id=transaction.user_id,
            amount=transaction.amount,
            merchant_id=transaction.merchant_id,
            merchant_name=transaction.merchant_name,
            category=transaction.category,
            location=transaction.location,
            timestamp=transaction.timestamp
        )
        
        # Recalculate fraud score
        new_fraud_score = await anomaly_detector.score_transaction(txn_data)
        
        # Update graph analysis
        graph_risk = await graph_analyzer.analyze_merchant_risk(
            transaction.merchant_id,
            transaction.user_id
        )
        
        # Update transaction
        transaction.fraud_score = new_fraud_score
        transaction.graph_risk_score = graph_risk.get("risk_score", 0.0)
        
        # Check if status should change
        is_flagged = new_fraud_score > 0.7 or graph_risk.get("risk_score", 0) > 0.8
        transaction.is_flagged = is_flagged
        transaction.status = "flagged" if is_flagged else "cleared"
        
        db.commit()
        
        logger.info(f"Transaction {transaction_id} rescored: {new_fraud_score}")
        
        return FraudScoreResponse(
            transaction_id=transaction_id,
            fraud_score=new_fraud_score,
            graph_risk_score=graph_risk.get("risk_score", 0.0),
            is_flagged=is_flagged,
            factors=graph_risk.get("factors", []),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error rescoring transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to rescore transaction")

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update transaction details (status, notes, etc.)
    """
    transaction = db.query(Transaction).filter(Transaction.txn_id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    return TransactionResponse.from_orm(transaction)

@router.get("/transactions/stats/summary")
async def get_transaction_stats(db: Session = Depends(get_db)):
    """
    Get transaction statistics for dashboard
    """
    try:
        total_transactions = db.query(Transaction).count()
        flagged_transactions = db.query(Transaction).filter(Transaction.is_flagged == True).count()
        
        # Calculate fraud rate
        fraud_rate = (flagged_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Calculate total amounts
        total_amount = db.query(Transaction).with_entities(
            db.func.sum(Transaction.amount)
        ).scalar() or 0
        
        flagged_amount = db.query(Transaction).filter(
            Transaction.is_flagged == True
        ).with_entities(
            db.func.sum(Transaction.amount)
        ).scalar() or 0
        
        return {
            "total_transactions": total_transactions,
            "flagged_transactions": flagged_transactions,
            "fraud_rate": round(fraud_rate, 2),
            "total_amount": total_amount,
            "flagged_amount": flagged_amount,
            "money_saved": flagged_amount
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get transaction statistics")