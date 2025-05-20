from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    schedule = Column(String, nullable=True)  # Cron expression for scheduling
    tasks = relationship("Task", back_populates="workflow", order_by="Task.order")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String, index=True)
    task_type = Column(String)  # email, api_call, file_upload, google_sheets, google_calendar, crm_update, employee_assignment
    config = Column(JSON)  # Task-specific configuration
    order = Column(Integer)  # Order of execution in workflow
    workflow = relationship("Workflow", back_populates="tasks")

    # Task type specific configurations
    # For email tasks
    email_to = Column(String, nullable=True)
    email_subject = Column(String, nullable=True)
    email_body = Column(Text, nullable=True)

    # For Google Sheets tasks
    spreadsheet_id = Column(String, nullable=True)
    sheet_name = Column(String, nullable=True)
    data_range = Column(String, nullable=True)

    # For Google Calendar tasks
    calendar_id = Column(String, nullable=True)
    event_title = Column(String, nullable=True)
    event_description = Column(Text, nullable=True)
    event_start = Column(DateTime, nullable=True)
    event_end = Column(DateTime, nullable=True)

    # For CRM update tasks
    crm_type = Column(String, nullable=True)  # salesforce, hubspot, etc.
    crm_object = Column(String, nullable=True)  # contact, lead, opportunity, etc.
    crm_action = Column(String, nullable=True)  # create, update, delete

    # For employee assignment tasks
    assignee_email = Column(String, nullable=True)
    assignment_title = Column(String, nullable=True)
    assignment_description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String)  # running, completed, failed
    error = Column(String, nullable=True)
    results = Column(JSON, nullable=True) 