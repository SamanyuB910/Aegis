from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import os
import uuid
from typing import Optional

from models.pydantic_schemas import ReceiptResponse, OCRResult, ForgeryAnalysis
from models.db_models import Receipt, get_db
from services.ocr_model import ReceiptOCRAnalyzer
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize OCR service
ocr_analyzer = ReceiptOCRAnalyzer()

# Upload directory
UPLOAD_DIR = "uploads/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_receipt", response_model=ReceiptResponse)
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    transaction_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload receipt file and perform OCR + forgery detection
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Receipt uploaded: {unique_filename}")
        
        # Create receipt record
        db_receipt = Receipt(
            transaction_id=transaction_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            content_type=file.content_type
        )
        
        # Perform OCR analysis
        ocr_result = await ocr_analyzer.analyze_receipt(file_path)
        
        # Update receipt with OCR results
        db_receipt.ocr_text = ocr_result.text
        db_receipt.extracted_amount = ocr_result.extracted_fields.get('amount')
        db_receipt.extracted_merchant = ocr_result.extracted_fields.get('merchant')
        db_receipt.extracted_date = ocr_result.extracted_fields.get('date')
        
        # Perform forgery detection
        forgery_result = await ocr_analyzer.detect_forgery(file_path, ocr_result)
        
        db_receipt.is_forged = forgery_result.is_forged
        db_receipt.forgery_confidence = forgery_result.confidence
        db_receipt.analysis_results = {
            "ocr_confidence": ocr_result.confidence,
            "anomalies": ocr_result.anomalies,
            "forgery_reasons": forgery_result.reasons,
            "technical_details": forgery_result.technical_details
        }
        
        # Calculate overall anomaly score
        anomaly_score = 0.0
        if forgery_result.is_forged:
            anomaly_score += forgery_result.confidence * 0.7
        
        if len(ocr_result.anomalies) > 0:
            anomaly_score += len(ocr_result.anomalies) * 0.1
        
        if ocr_result.confidence < 0.5:  # Low OCR confidence
            anomaly_score += 0.2
        
        db_receipt.anomaly_score = min(1.0, anomaly_score)
        
        # Save to database
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        
        logger.info(f"Receipt {db_receipt.receipt_id} processed: anomaly_score={anomaly_score:.3f}")
        
        # Send real-time alert if high anomaly score
        if anomaly_score > 0.7:
            alert_data = {
                "type": "receipt_anomaly",
                "receipt_id": db_receipt.receipt_id,
                "transaction_id": transaction_id,
                "anomaly_score": anomaly_score,
                "is_forged": forgery_result.is_forged,
                "confidence": forgery_result.confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "critical" if anomaly_score > 0.9 else "high"
            }
            background_tasks.add_task(websocket_manager.broadcast_alert, alert_data)
        
        return ReceiptResponse.from_orm(db_receipt)
        
    except Exception as e:
        logger.error(f"❌ Receipt upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Receipt processing failed: {str(e)}")

@router.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """Get receipt by ID"""
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return ReceiptResponse.from_orm(receipt)

@router.post("/receipts/{receipt_id}/reanalyze", response_model=ReceiptResponse)
async def reanalyze_receipt(
    receipt_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reanalyze receipt for OCR and forgery detection"""
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    try:
        # Re-run OCR analysis
        ocr_result = await ocr_analyzer.analyze_receipt(receipt.file_path)
        
        # Update OCR fields
        receipt.ocr_text = ocr_result.text
        receipt.extracted_amount = ocr_result.extracted_fields.get('amount')
        receipt.extracted_merchant = ocr_result.extracted_fields.get('merchant')
        receipt.extracted_date = ocr_result.extracted_fields.get('date')
        
        # Re-run forgery detection
        forgery_result = await ocr_analyzer.detect_forgery(receipt.file_path, ocr_result)
        
        receipt.is_forged = forgery_result.is_forged
        receipt.forgery_confidence = forgery_result.confidence
        receipt.analysis_results = {
            "ocr_confidence": ocr_result.confidence,
            "anomalies": ocr_result.anomalies,
            "forgery_reasons": forgery_result.reasons,
            "technical_details": forgery_result.technical_details
        }
        
        # Recalculate anomaly score
        anomaly_score = 0.0
        if forgery_result.is_forged:
            anomaly_score += forgery_result.confidence * 0.7
        
        if len(ocr_result.anomalies) > 0:
            anomaly_score += len(ocr_result.anomalies) * 0.1
        
        if ocr_result.confidence < 0.5:
            anomaly_score += 0.2
        
        receipt.anomaly_score = min(1.0, anomaly_score)
        receipt.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Receipt {receipt_id} reanalyzed: anomaly_score={anomaly_score:.3f}")
        
        return ReceiptResponse.from_orm(receipt)
        
    except Exception as e:
        logger.error(f"❌ Receipt reanalysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Receipt reanalysis failed: {str(e)}")

@router.get("/receipts/transaction/{transaction_id}")
async def get_receipts_by_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get all receipts for a transaction"""
    receipts = db.query(Receipt).filter(Receipt.transaction_id == transaction_id).all()
    
    return [ReceiptResponse.from_orm(receipt) for receipt in receipts]

@router.post("/receipts/{receipt_id}/verify")
async def verify_receipt_against_transaction(
    receipt_id: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Verify receipt details against transaction data"""
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # This would typically fetch transaction data from the database
    # For now, we'll return a verification result based on the receipt analysis
    
    verification_result = {
        "receipt_id": receipt_id,
        "transaction_id": transaction_id,
        "verification_status": "verified" if not receipt.is_forged else "failed",
        "confidence": 1.0 - receipt.anomaly_score,
        "discrepancies": [],
        "verification_timestamp": datetime.utcnow().isoformat()
    }
    
    # Check for discrepancies (simplified logic)
    discrepancies = []
    
    if receipt.anomaly_score > 0.5:
        discrepancies.append("High anomaly score detected")
    
    if receipt.is_forged:
        discrepancies.append("Receipt appears to be forged")
    
    if receipt.extracted_amount and receipt.extracted_amount < 0:
        discrepancies.append("Invalid amount extracted")
    
    verification_result["discrepancies"] = discrepancies
    
    if discrepancies:
        verification_result["verification_status"] = "failed"
    
    return verification_result