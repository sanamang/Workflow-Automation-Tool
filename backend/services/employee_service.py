from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmployeeService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def create_assignment(self, assignee_email: str, title: str, description: str, due_date: datetime) -> bool:
        """Create and send an employee assignment."""
        try:
            if not all([self.smtp_username, self.smtp_password]):
                raise ValueError("SMTP credentials not configured")

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = assignee_email
            msg['Subject'] = f"New Assignment: {title}"

            # Create email body
            body = f"""
            <h2>New Assignment</h2>
            <p><strong>Title:</strong> {title}</p>
            <p><strong>Description:</strong> {description}</p>
            <p><strong>Due Date:</strong> {due_date.strftime('%Y-%m-%d %H:%M')}</p>
            <p>Please log in to the Workflow Automation system to view more details.</p>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error creating employee assignment: {str(e)}")
            return False

    def update_assignment(self, assignment_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing employee assignment."""
        try:
            # Here you would typically update the assignment in your database
            # For now, we'll just return True as a placeholder
            return True
        except Exception as e:
            print(f"Error updating employee assignment: {str(e)}")
            return False

    def get_assignment_status(self, assignment_id: str) -> Dict[str, Any]:
        """Get the status of an employee assignment."""
        try:
            # Here you would typically fetch the assignment status from your database
            # For now, we'll return a placeholder status
            return {
                'status': 'pending',
                'last_updated': datetime.now().isoformat(),
                'progress': 0
            }
        except Exception as e:
            print(f"Error getting assignment status: {str(e)}")
            return {} 