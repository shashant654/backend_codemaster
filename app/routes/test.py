from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.db.database import get_db
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

router = APIRouter(
    prefix="/api/v1/test",
    tags=["test"]
)

logger = logging.getLogger(__name__)

class EmailTestRequest(BaseModel):
    recipient_email: EmailStr
    subject: str = "Test Email from CodeMaster"
    message: str = "This is a test email to verify SMTP configuration"

class AdminEmailTestRequest(BaseModel):
    subject: str = "Test Email to Admin"
    message: str = "This is a test email to admin"

@router.post("/send-email")
async def test_send_email(email_request: EmailTestRequest):
    """
    Test endpoint to send a test email using configured SMTP settings.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = email_request.recipient_email
        msg['Subject'] = email_request.subject

        body = f"""
        <html>
            <body>
                <h2>Test Email</h2>
                <p>{email_request.message}</p>
                <br>
                <p><strong>SMTP Configuration:</strong></p>
                <ul>
                    <li>Host: {settings.EMAIL_HOST}</li>
                    <li>Port: {settings.EMAIL_PORT}</li>
                    <li>From: {settings.DEFAULT_FROM_EMAIL}</li>
                </ul>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP Server
        if settings.EMAIL_PORT == 465:
            # Use SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        else:
            # Use SMTP with STARTTLS for port 587 and others
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            server.starttls()
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Test email sent to {email_request.recipient_email}")
        return {
            "success": True,
            "message": f"Test email sent successfully to {email_request.recipient_email}",
            "smtp_config": {
                "host": settings.EMAIL_HOST,
                "port": settings.EMAIL_PORT,
                "from_email": settings.DEFAULT_FROM_EMAIL
            }
        }
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed - check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        raise HTTPException(
            status_code=500,
            detail="SMTP Authentication failed. Please check your email credentials."
        )
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SMTP error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )

@router.get("/email-config")
async def get_email_config():
    """
    Get current email configuration (for debugging).
    Note: PASSWORD is masked for security.
    """
    return {
        "email_host": settings.EMAIL_HOST,
        "email_port": settings.EMAIL_PORT,
        "email_host_user": settings.EMAIL_HOST_USER,
        "email_host_password": "***" if settings.EMAIL_HOST_PASSWORD else "Not configured",
        "default_from_email": settings.DEFAULT_FROM_EMAIL
    }

@router.post("/send-email-to-admin")
async def send_email_to_admin(
    email_request: AdminEmailTestRequest,
    db: Session = Depends(get_db)
):
    """
    Test endpoint to send email to admin user (is_admin=True).
    Only requires subject and message.
    """
    try:
        # Get admin from database
        from app.models.models import User
        admin = db.query(User).filter(User.is_admin == True).first()
        
        if not admin:
            raise HTTPException(
                status_code=404,
                detail="No admin user found in database"
            )
        
        admin_email = admin.email
        logger.info(f"Found admin user with email: {admin_email}")
        
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = admin_email
        msg['Subject'] = email_request.subject

        body = f"""
        <html>
            <body>
                <h2>Test Email to Admin</h2>
                <p>{email_request.message}</p>
                <br>
                <p><strong>Admin Email:</strong> {admin_email}</p>
                <p><strong>SMTP Configuration:</strong></p>
                <ul>
                    <li>Host: {settings.EMAIL_HOST}</li>
                    <li>Port: {settings.EMAIL_PORT}</li>
                    <li>From: {settings.DEFAULT_FROM_EMAIL}</li>
                </ul>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP Server
        if settings.EMAIL_PORT == 465:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            server.starttls()
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Test email sent to admin: {admin_email}")
        return {
            "success": True,
            "message": f"Test email sent successfully to admin: {admin_email}",
            "admin_email": admin_email,
            "smtp_config": {
                "host": settings.EMAIL_HOST,
                "port": settings.EMAIL_PORT,
                "from_email": settings.DEFAULT_FROM_EMAIL
            }
        }
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="SMTP Authentication failed. Please check your email credentials."
        )
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SMTP error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to send admin email: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )
