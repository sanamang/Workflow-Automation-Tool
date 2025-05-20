from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Execution, Workflow
from schemas import ExecutionResponse

router = APIRouter()

@router.get("/workflow/{workflow_id}", response_model=List[ExecutionResponse])
def list_workflow_executions(workflow_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Verify workflow exists
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    executions = db.query(Execution).filter(
        Execution.workflow_id == workflow_id
    ).order_by(Execution.started_at.desc()).offset(skip).limit(limit).all()
    return executions

@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.get("/", response_model=List[ExecutionResponse])
def list_all_executions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    executions = db.query(Execution).order_by(
        Execution.started_at.desc()
    ).offset(skip).limit(limit).all()
    return executions 