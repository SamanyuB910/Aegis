from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import asyncio
import random
import numpy as np

from models.pydantic_schemas import SpellRequest, SpellResult, SpellType
from models.db_models import SpellRun, get_db
from services.spell_simulator import SpellSimulator
from services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize spell simulator
spell_simulator = SpellSimulator()

@router.post("/run_spell", response_model=SpellResult)
async def run_spell(
    spell_request: SpellRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a fraud simulation spell
    """
    try:
        # Create spell run record
        db_spell_run = SpellRun(
            spell_name=spell_request.spell_name.value,
            spell_type=spell_request.spell_name.value,
            parameters=spell_request.dict(),
            status="running"
        )
        
        db.add(db_spell_run)
        db.commit()
        db.refresh(db_spell_run)
        
        logger.info(f"Starting spell: {spell_request.spell_name.value} ({db_spell_run.run_id})")
        
        # Execute spell simulation
        spell_result = await spell_simulator.execute_spell(
            spell_request.spell_name,
            spell_request.context,
            spell_request.parameters
        )
        
        # Update spell run with results
        db_spell_run.status = "completed"
        db_spell_run.progress = 100.0
        db_spell_run.affected_transactions = spell_result.get("affected_transactions", 0)
        db_spell_run.flagged_transactions = spell_result.get("flagged_transactions", 0)
        db_spell_run.total_impact = spell_result.get("total_impact", 0.0)
        db_spell_run.results = spell_result
        db_spell_run.completed_at = datetime.utcnow()
        db_spell_run.duration_seconds = (
            db_spell_run.completed_at - db_spell_run.started_at
        ).total_seconds()
        
        db.commit()
        
        # Broadcast spell results via WebSocket
        websocket_data = {
            "type": "spell_completed",
            "run_id": db_spell_run.run_id,
            "spell_name": spell_request.spell_name.value,
            "results": spell_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        background_tasks.add_task(websocket_manager.broadcast_spell_result, websocket_data)
        
        # Generate fraud alerts for flagged transactions
        if spell_result.get("flagged_transactions", 0) > 0:
            alert_data = {
                "type": "spell_alert",
                "spell_name": spell_request.spell_name.value,
                "flagged_count": spell_result.get("flagged_transactions"),
                "severity": "critical" if spell_result.get("flagged_transactions", 0) > 10 else "high",
                "timestamp": datetime.utcnow().isoformat()
            }
            background_tasks.add_task(websocket_manager.broadcast_alert, alert_data)
        
        return SpellResult(
            run_id=db_spell_run.run_id,
            spell_name=db_spell_run.spell_name,
            status=db_spell_run.status,
            progress=db_spell_run.progress,
            affected_transactions=db_spell_run.affected_transactions,
            flagged_transactions=db_spell_run.flagged_transactions,
            total_impact=db_spell_run.total_impact,
            results=db_spell_run.results,
            started_at=db_spell_run.started_at,
            completed_at=db_spell_run.completed_at,
            duration_seconds=db_spell_run.duration_seconds
        )
        
    except Exception as e:
        # Update spell run status to failed
        if 'db_spell_run' in locals():
            db_spell_run.status = "failed"
            db_spell_run.results = {"error": str(e)}
            db.commit()
        
        logger.error(f"❌ Spell execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Spell execution failed: {str(e)}")

@router.get("/spells/{run_id}", response_model=SpellResult)
async def get_spell_result(run_id: str, db: Session = Depends(get_db)):
    """Get spell run results by ID"""
    spell_run = db.query(SpellRun).filter(SpellRun.run_id == run_id).first()
    
    if not spell_run:
        raise HTTPException(status_code=404, detail="Spell run not found")
    
    return SpellResult(
        run_id=spell_run.run_id,
        spell_name=spell_run.spell_name,
        status=spell_run.status,
        progress=spell_run.progress,
        affected_transactions=spell_run.affected_transactions,
        flagged_transactions=spell_run.flagged_transactions,
        total_impact=spell_run.total_impact,
        results=spell_run.results or {},
        started_at=spell_run.started_at,
        completed_at=spell_run.completed_at,
        duration_seconds=spell_run.duration_seconds
    )

@router.get("/spells")
async def list_spell_runs(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List recent spell runs"""
    query = db.query(SpellRun)
    
    if status:
        query = query.filter(SpellRun.status == status)
    
    spell_runs = query.order_by(SpellRun.started_at.desc()).offset(skip).limit(limit).all()
    
    return [
        SpellResult(
            run_id=run.run_id,
            spell_name=run.spell_name,
            status=run.status,
            progress=run.progress,
            affected_transactions=run.affected_transactions,
            flagged_transactions=run.flagged_transactions,
            total_impact=run.total_impact,
            results=run.results or {},
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_seconds=run.duration_seconds
        )
        for run in spell_runs
    ]

@router.get("/spells/types/available")
async def get_available_spell_types():
    """Get list of available spell types"""
    return {
        "spell_types": [
            {
                "name": "rug_pull",
                "display_name": "Rug Pull Attack",
                "description": "Simulates a merchant suddenly disappearing with customer funds",
                "risk_level": "critical",
                "estimated_duration": "5-10 minutes"
            },
            {
                "name": "oracle_manipulation",
                "display_name": "Oracle Price Manipulation",
                "description": "Simulates manipulation of price feeds affecting transaction values",
                "risk_level": "high", 
                "estimated_duration": "10-15 minutes"
            },
            {
                "name": "sybil_attack",
                "display_name": "Sybil Account Attack",
                "description": "Simulates creation of multiple fake accounts for fraud",
                "risk_level": "high",
                "estimated_duration": "15-20 minutes"
            },
            {
                "name": "flash_loan_attack",
                "display_name": "Flash Loan Exploitation",
                "description": "Simulates flash loan attacks on DeFi protocols",
                "risk_level": "critical",
                "estimated_duration": "3-5 minutes"
            },
            {
                "name": "merchant_collusion",
                "display_name": "Merchant Collusion Network",
                "description": "Simulates coordinated fraud across merchant network",
                "risk_level": "high",
                "estimated_duration": "20-30 minutes"
            }
        ]
    }

@router.post("/spells/{run_id}/cancel")
async def cancel_spell(run_id: str, db: Session = Depends(get_db)):
    """Cancel a running spell"""
    spell_run = db.query(SpellRun).filter(SpellRun.run_id == run_id).first()
    
    if not spell_run:
        raise HTTPException(status_code=404, detail="Spell run not found")
    
    if spell_run.status != "running":
        raise HTTPException(status_code=400, detail="Spell is not currently running")
    
    # Update status to cancelled
    spell_run.status = "cancelled"
    spell_run.completed_at = datetime.utcnow()
    spell_run.duration_seconds = (
        spell_run.completed_at - spell_run.started_at
    ).total_seconds()
    
    db.commit()
    
    logger.info(f"Spell {run_id} cancelled")
    
    return {"message": f"Spell {run_id} has been cancelled"}

@router.get("/spells/stats/summary")
async def get_spell_stats(db: Session = Depends(get_db)):
    """Get spell execution statistics"""
    try:
        total_runs = db.query(SpellRun).count()
        completed_runs = db.query(SpellRun).filter(SpellRun.status == "completed").count()
        failed_runs = db.query(SpellRun).filter(SpellRun.status == "failed").count()
        running_runs = db.query(SpellRun).filter(SpellRun.status == "running").count()
        
        # Calculate success rate
        success_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Get most common spell types
        spell_type_counts = db.query(SpellRun.spell_type, db.func.count(SpellRun.id)).group_by(SpellRun.spell_type).all()
        
        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "failed_runs": failed_runs,
            "running_runs": running_runs,
            "success_rate": round(success_rate, 2),
            "spell_type_distribution": [
                {"spell_type": spell_type, "count": count}
                for spell_type, count in spell_type_counts
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting spell stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get spell statistics")