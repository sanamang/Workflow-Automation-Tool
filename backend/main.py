from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
from database import engine, SessionLocal
from services.google_service import GoogleService
from services.crm_service import CRMService
from services.employee_service import EmployeeService
from datetime import datetime
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize services
google_service = GoogleService()
crm_service = CRMService()
employee_service = EmployeeService()

@app.get("/")
async def root():
    return {"message": "Workflow Automation API"}

@app.get("/workflows/", response_model=List[models.Workflow])
def get_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = db.query(models.Workflow).offset(skip).limit(limit).all()
    return workflows

@app.post("/workflows/", response_model=models.Workflow)
def create_workflow(workflow: models.WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = models.Workflow(
        name=workflow.name,
        description=workflow.description,
        is_active=workflow.is_active,
        schedule=workflow.schedule
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@app.get("/workflows/{workflow_id}", response_model=models.Workflow)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.post("/workflows/{workflow_id}/tasks/", response_model=models.Task)
def create_task(workflow_id: int, task: models.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(
        workflow_id=workflow_id,
        name=task.name,
        task_type=task.task_type,
        config=task.config,
        order=task.order,
        email_to=task.email_to,
        email_subject=task.email_subject,
        email_body=task.email_body,
        spreadsheet_id=task.spreadsheet_id,
        sheet_name=task.sheet_name,
        calendar_id=task.calendar_id,
        event_title=task.event_title,
        event_description=task.event_description,
        event_start=task.event_start,
        event_end=task.event_end,
        crm_type=task.crm_type,
        crm_object=task.crm_object,
        crm_action=task.crm_action,
        assignee_email=task.assignee_email,
        assignment_title=task.assignment_title,
        assignment_description=task.assignment_description,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/workflows/{workflow_id}/execute/")
def execute_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    execution = models.Execution(
        workflow_id=workflow_id,
        started_at=datetime.utcnow(),
        status="running"
    )
    db.add(execution)
    db.commit()

    try:
        tasks = db.query(models.Task).filter(models.Task.workflow_id == workflow_id).order_by(models.Task.order).all()
        results = []

        for task in tasks:
            task_result = {"task_id": task.id, "status": "success"}
            
            try:
                if task.task_type == "email":
                    # Handle email task
                    pass
                elif task.task_type == "google_sheets":
                    success = google_service.update_google_sheet(
                        task.spreadsheet_id,
                        task.sheet_name,
                        json.loads(task.config)
                    )
                    if not success:
                        raise Exception("Failed to update Google Sheet")
                elif task.task_type == "google_calendar":
                    success = google_service.create_calendar_event(
                        task.calendar_id,
                        {
                            "title": task.event_title,
                            "description": task.event_description,
                            "start": task.event_start.isoformat(),
                            "end": task.event_end.isoformat()
                        }
                    )
                    if not success:
                        raise Exception("Failed to create calendar event")
                elif task.task_type == "crm_update":
                    success = crm_service.update_crm(
                        task.crm_type,
                        task.crm_object,
                        task.crm_action,
                        json.loads(task.config)
                    )
                    if not success:
                        raise Exception("Failed to update CRM")
                elif task.task_type == "employee_assignment":
                    success = employee_service.create_assignment(
                        task.assignee_email,
                        task.assignment_title,
                        task.assignment_description,
                        task.due_date
                    )
                    if not success:
                        raise Exception("Failed to create employee assignment")
                
                results.append(task_result)
            except Exception as e:
                task_result["status"] = "failed"
                task_result["error"] = str(e)
                results.append(task_result)
                break

        execution.completed_at = datetime.utcnow()
        execution.status = "completed" if all(r["status"] == "success" for r in results) else "failed"
        execution.results = results
        db.commit()

        return {"status": execution.status, "results": results}
    except Exception as e:
        execution.completed_at = datetime.utcnow()
        execution.status = "failed"
        execution.error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e)) 