from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Workflow, Task, Execution
from schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from datetime import datetime
import json

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        schedule=workflow.schedule
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = db.query(Workflow).offset(skip).limit(limit).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, workflow: WorkflowUpdate, db: Session = Depends(get_db)):
    db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    for key, value in workflow.dict(exclude_unset=True).items():
        setattr(db_workflow, key, value)
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute")
def execute_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create execution record
    execution = Execution(
        workflow_id=workflow_id,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    
    try:
        # Get tasks in order
        tasks = db.query(Task).filter(Task.workflow_id == workflow_id).order_by(Task.order).all()
        results = []
        
        for task in tasks:
            # Execute task based on type
            if task.task_type == "email":
                # Implement email sending logic
                pass
            elif task.task_type == "api_call":
                # Implement API call logic
                pass
            elif task.task_type == "file_upload":
                # Implement file upload logic
                pass
            
            results.append({
                "task_id": task.id,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.results = json.dumps(results)
        
    except Exception as e:
        execution.status = "failed"
        execution.error = str(e)
        execution.completed_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Workflow execution completed", "execution_id": execution.id} 