import time
import logging
from celery import Task
from datetime import datetime
import random

from celery_app import app

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_app")


class EmailTask(Task):
    """Custom Celery Task class for email jobs"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"❌ Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"✅ Task {task_id} completed successfully")
        super().on_success(retval, task_id, args, kwargs)

    def get_timestamp(self):
        return datetime.utcnow().isoformat()

    def update_progress(self, current, total, status_message="Processing"):
        progress = int((current / total) * 100) if total > 0 else 0
        self.update_state(
            state="PROGRESS",
            meta={
                "current": current,
                "total": total,
                "progress": progress,
                "status": status_message,
                "timestamp": self.get_timestamp(),
            },
        )


@app.task(bind=True, base=EmailTask, name="tasks.send_single_email")
def send_single_email(self, recipient_email, subject, message):
    """Send a single email in the background"""
    try:
        task_id = self.request.id
        logger.info(f"📧 Starting email task {task_id} to {recipient_email}")

        # Step 1: Validate email
        self.update_state(
            state="PROCESSING",
            meta={"status": "Validating email address", "step": "1/5"},
        )
        time.sleep(1)

        if "@" not in recipient_email:
            raise ValueError("Invalid email address")

        # Step 2: Prepare content
        self.update_state(
            state="PROCESSING",
            meta={"status": "Preparing email content", "step": "2/5"},
        )
        time.sleep(1)

        # Step 3: Connect to server
        self.update_state(
            state="CONNECTING",
            meta={"status": "Connecting to email server", "step": "3/5"},
        )
        time.sleep(2)

        # Step 4: Send email
        self.update_state(
            state="SENDING", meta={"status": "Sending email", "step": "4/5"}
        )

        success = simulate_email_sending(recipient_email, subject, message)

        if not success:
            raise Exception("Failed to send email")

        # Step 5: Verify
        self.update_state(
            state="FINALIZING", meta={"status": "Verifying delivery", "step": "5/5"}
        )
        time.sleep(0.5)

        result = {
            "status": "COMPLETED",
            "recipient": recipient_email,
            "subject": subject,
            "sent_at": self.get_timestamp(),
            "task_id": task_id,
            "message": "Email sent successfully!",
        }

        logger.info(f"✅ Email sent successfully to {recipient_email}")
        return result

    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        raise


@app.task(bind=True, base=EmailTask, name="tasks.send_bulk_emails")
def send_bulk_emails(self, email_list, subject, message):
    """Send emails to multiple recipients"""
    try:
        task_id = self.request.id
        total_emails = len(email_list)
        logger.info(
            f"📧 Starting bulk email task {task_id} for {total_emails} recipients"
        )

        self.update_progress(0, total_emails, "Starting bulk email send")

        sent_emails = []
        failed_emails = []

        for i, email in enumerate(email_list):
            current_step = i + 1

            self.update_progress(
                current_step,
                total_emails,
                f"Sending email {current_step}/{total_emails} to {email}",
            )

            try:
                success = simulate_email_sending(email, subject, message)

                if success:
                    sent_emails.append(email)
                    logger.info(
                        f"✅ Email {current_step}/{total_emails} sent to {email}"
                    )
                else:
                    failed_emails.append(email)
                    logger.warning(
                        f"❌ Email {current_step}/{total_emails} failed for {email}"
                    )

                time.sleep(1.5)

            except Exception as e:
                failed_emails.append(email)
                logger.error(f"❌ Error sending email to {email}: {str(e)}")

        # Final result
        success_rate = (len(sent_emails) / total_emails) * 100

        result = {
            "status": "COMPLETED",
            "total_emails": total_emails,
            "sent_count": len(sent_emails),
            "failed_count": len(failed_emails),
            "success_rate": f"{success_rate:.1f}%",
            "sent_emails": sent_emails,
            "failed_emails": failed_emails,
            "subject": subject,
            "completed_at": self.get_timestamp(),
            "task_id": task_id,
        }

        logger.info(
            f"📧 Bulk email task completed: {len(sent_emails)}/{total_emails} sent"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Error in bulk email task: {str(e)}")
        raise


def simulate_email_sending(recipient, subject, message):
    """Simulate sending an email (replace with real email logic)"""
    # Simulate processing time
    time.sleep(random.uniform(1.0, 3.0))

    # Simulate 10% failure rate for demo
    if random.random() < 0.1:
        return False

    logger.info(f"📨 [SIMULATED] Email sent to {recipient}")
    return True
