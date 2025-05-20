from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database import get_db
from models import Workflow
from routers.workflows import execute_workflow
import asyncio

scheduler = AsyncIOScheduler()

async def schedule_workflow(workflow_id: int, cron_expression: str):
    """Schedule a workflow to run based on a cron expression"""
    trigger = CronTrigger.from_crontab(cron_expression)
    scheduler.add_job(
        execute_workflow,
        trigger=trigger,
        args=[workflow_id],
        id=f"workflow_{workflow_id}"
    )

async def unschedule_workflow(workflow_id: int):
    """Remove a workflow from the scheduler"""
    job_id = f"workflow_{workflow_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

async def initialize_scheduler():
    """Initialize the scheduler and load existing scheduled workflows"""
    scheduler.start()
    
    # Get database session
    db = next(get_db())
    try:
        # Load all active workflows with schedules
        workflows = db.query(Workflow).filter(
            Workflow.is_active == True,
            Workflow.schedule.isnot(None)
        ).all()
        
        # Schedule each workflow
        for workflow in workflows:
            await schedule_workflow(workflow.id, workflow.schedule)
    finally:
        db.close()

def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown() 