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
    """Send a single email in the background - FIXED VERSION (No failures)"""
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

        # Step 4: Send email (FIXED - Always succeeds)
        self.update_state(
            state="SENDING", meta={"status": "Sending email", "step": "4/5"}
        )

        # FIXED: Always successful email sending
        success = simulate_email_sending_fixed(recipient_email, subject, message)

        # Since we fixed the function, this should never fail
        if not success:
            raise Exception("Unexpected email sending failure")

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
            "delivery_status": "confirmed",
        }

        logger.info(f"✅ Email sent successfully to {recipient_email}")
        return result

    except ValueError as e:
        # Only fails for invalid email addresses
        logger.error(f"❌ Invalid email address: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error sending email: {str(e)}")
        raise


@app.task(bind=True, base=EmailTask, name="tasks.send_bulk_emails")
def send_bulk_emails(self, email_list, subject, message):
    """Send emails to multiple recipients - FIXED VERSION (No failures)"""
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
                # Validate email before sending
                if "@" not in email or "." not in email.split("@")[-1]:
                    failed_emails.append(
                        {
                            "email": email,
                            "failed_at": self.get_timestamp(),
                            "reason": "Invalid email format",
                        }
                    )
                    logger.warning(f"❌ Invalid email format: {email}")
                    continue

                # FIXED: Always successful email sending
                success = simulate_email_sending_fixed(email, subject, message)

                if success:
                    sent_emails.append(
                        {
                            "email": email,
                            "sent_at": self.get_timestamp(),
                            "status": "success",
                        }
                    )
                    logger.info(
                        f"✅ Email {current_step}/{total_emails} sent to {email}"
                    )
                else:
                    # This should never happen with the fixed function
                    failed_emails.append(
                        {
                            "email": email,
                            "failed_at": self.get_timestamp(),
                            "reason": "Unexpected sending failure",
                        }
                    )

                # Small delay between emails
                time.sleep(1)

            except Exception as e:
                failed_emails.append(
                    {
                        "email": email,
                        "failed_at": self.get_timestamp(),
                        "reason": str(e),
                    }
                )
                logger.error(f"❌ Error sending email to {email}: {str(e)}")

        # Calculate statistics
        success_rate = (
            (len(sent_emails) / total_emails) * 100 if total_emails > 0 else 0
        )

        # Final result
        result = {
            "status": "COMPLETED",
            "summary": {
                "total_emails": total_emails,
                "sent_count": len(sent_emails),
                "failed_count": len(failed_emails),
                "success_rate": f"{success_rate:.1f}%",
            },
            "sent_emails": sent_emails,
            "failed_emails": failed_emails,
            "subject": subject,
            "completed_at": self.get_timestamp(),
            "task_id": task_id,
        }

        logger.info(
            f"📧 Bulk email task completed: {len(sent_emails)}/{total_emails} sent ({success_rate:.1f}% success rate)"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Error in bulk email task: {str(e)}")
        raise


def simulate_email_sending_fixed(recipient, subject, message):
    """
    FIXED: Simulate sending an email - Always successful
    No more random failures!
    """
    # Simulate realistic email sending time
    processing_time = random.uniform(1.0, 3.0)
    time.sleep(processing_time)

    # FIXED: Always return success (no more 10% failure rate)
    logger.info(f"📨 [SIMULATED] Email sent to {recipient}")
    logger.debug(f"   Subject: {subject}")
    logger.debug(f"   Message preview: {message[:50]}...")
    logger.debug(f"   Processing time: {processing_time:.2f}s")

    return True  # Always successful


# Optional: Function for real email sending (commented out)
"""
def send_real_email(recipient, subject, message):
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        raise ValueError("Email credentials not configured")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        logger.info(f"📨 [REAL] Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"❌ [REAL] Email sending failed: {e}")
        return False
"""
