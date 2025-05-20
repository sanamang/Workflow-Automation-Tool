from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    schedule: Optional[str] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(WorkflowBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class WorkflowResponse(WorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    name: str
    task_type: str
    config: Dict[str, Any]
    order: int

class TaskCreate(TaskBase):
    workflow_id: int

class TaskUpdate(TaskBase):
    name: Optional[str] = None
    task_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    order: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    workflow_id: int

    class Config:
        orm_mode = True

class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    error: Optional[str]
    results: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True 