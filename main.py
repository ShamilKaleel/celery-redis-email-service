import logging
import os
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from celery_app import get_queue_length, app as celery_app
from tasks import send_single_email, send_bulk_emails

load_dotenv()

# Configuration
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", "8000"))
MAX_QUEUE_LENGTH_SINGLE = int(os.getenv("MAX_QUEUE_LENGTH_SINGLE", "50"))
MAX_QUEUE_LENGTH_BULK = int(os.getenv("MAX_QUEUE_LENGTH_BULK", "30"))
MAX_BULK_EMAILS = int(os.getenv("MAX_BULK_EMAILS", "100"))
FLOWER_PORT = os.getenv("FLOWER_PORT", "5555")

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("email_app")

app = FastAPI(
    title="📧 Email Service API",
    description="Send emails in the background using Celery + Redis + Flower with UV",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class SingleEmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    message: str


class BulkEmailRequest(BaseModel):
    email_list: List[EmailStr]
    subject: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    meta: Optional[dict] = None


@app.get("/")
def read_root():
    return {
        "message": "📧 Email Service API is running with UV!",
        "flower_dashboard": f"http://localhost:{FLOWER_PORT}",
        "endpoints": {
            "send_email": "POST /send-email",
            "send_bulk": "POST /send-bulk-emails",
            "check_status": "GET /task/{task_id}",
            "queue_status": "GET /queue-status",
        },
        "tech_stack": {
            "web_framework": "FastAPI",
            "task_queue": "Celery",
            "message_broker": "Redis",
            "monitoring": "Flower",
        },
    }


@app.get("/queue-status")
def get_queue_status():
    """Check how many tasks are in the queue"""
    queue_length = get_queue_length()
    status = "healthy" if queue_length < MAX_QUEUE_LENGTH_SINGLE else "busy"

    return {
        "queue_length": queue_length,
        "message": f"There are {queue_length} tasks waiting in the queue",
        "status": status,
    }


@app.post("/send-email")
def send_email_endpoint(request: SingleEmailRequest) -> JSONResponse:
    """Send a single email in the background"""
    try:
        current_queue_length = get_queue_length()

        if current_queue_length >= MAX_QUEUE_LENGTH_SINGLE:
            return JSONResponse(
                content={
                    "error": "Email queue is full. Please try again later.",
                    "queue_length": current_queue_length,
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        task = send_single_email.delay(
            request.recipient_email, request.subject, request.message
        )

        logger.info(f"📧 Email task started: {task.id}")

        return JSONResponse(
            content={
                "task_id": task.id,
                "status": "PENDING",
                "message": f"Email to {request.recipient_email} is being sent in background",
                "recipient": request.recipient_email,
                "subject": request.subject,
                "flower_url": f"http://localhost:{FLOWER_PORT}/task/{task.id}",
            }
        )

    except Exception as e:
        logger.error(f"Error starting email task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start email task: {str(e)}",
        )


@app.post("/send-bulk-emails")
def send_bulk_emails_endpoint(request: BulkEmailRequest) -> JSONResponse:
    """Send emails to multiple recipients in the background"""
    try:
        if len(request.email_list) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email list cannot be empty",
            )

        if len(request.email_list) > MAX_BULK_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot send more than {MAX_BULK_EMAILS} emails at once",
            )

        current_queue_length = get_queue_length()

        if current_queue_length >= MAX_QUEUE_LENGTH_BULK:
            return JSONResponse(
                content={
                    "error": "Email queue is full. Please try again later.",
                    "queue_length": current_queue_length,
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        task = send_bulk_emails.delay(
            request.email_list, request.subject, request.message
        )

        logger.info(
            f"📧 Bulk email task started: {task.id} for {len(request.email_list)} recipients"
        )

        return JSONResponse(
            content={
                "task_id": task.id,
                "status": "PENDING",
                "message": f"Bulk email to {len(request.email_list)} recipients is being sent in background",
                "recipient_count": len(request.email_list),
                "subject": request.subject,
                "flower_url": f"http://localhost:{FLOWER_PORT}/task/{task.id}",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk email task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start bulk email task: {str(e)}",
        )


@app.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> JSONResponse:
    """Check the status of an email task"""
    try:
        task_result = celery_app.AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": task_result.status,
        }

        if task_result.status == "PROGRESS":
            response_data["meta"] = task_result.info
        elif task_result.successful():
            response_data["result"] = task_result.result
            response_data["status"] = "COMPLETED"
        elif task_result.failed():
            response_data["status"] = "FAILED"
            error_msg = str(task_result.result) if task_result.result else "Task failed"
            response_data["error"] = error_msg

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error fetching task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
