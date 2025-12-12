import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

def send_payment_notification(order_id: int, amount: float, user_email: str, proof_url: str, utr: str):
    """
    Send an email notification to the Admin about a new manual UPI payment.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = settings.EMAIL_HOST_USER # Send to Admin (Host User)
        msg['Subject'] = f"New Manual Payment Verification - Order #{order_id}"

        body = f"""
        <html>
            <body>
                <h2>New Payment Verification Request</h2>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>User Email:</strong> {user_email}</p>
                <p><strong>Amount:</strong> ₹{amount}</p>
                <p><strong>UTR / Transaction ID:</strong> {utr}</p>
                <p><strong>Payment Proof:</strong> <a href="{proof_url}">View Screenshot</a></p>
                <br>
                <p>Please log in to the Admin Panel to verify this order.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP Server
        if settings.EMAIL_PORT == 465:
            # Use SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            # Use SMTP with STARTTLS for port 587 and others
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Payment notification email sent for Order #{order_id}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_order_status_email(user_email: str, order_id: int, status: str):
    """
    Send an email notification to the User about their order status update.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = user_email
        
        subject_status = "Approved" if status == "completed" else "Rejected"
        msg['Subject'] = f"Payment Update - Order #{order_id} {subject_status}"

        color = "#22c55e" if status == "completed" else "#ef4444" 
        message_text = "Your payment has been verified and your courses are now available!" if status == "completed" else "Your payment verification failed. Please contact support."

        body = f"""
        <html>
            <body>
                <h2>Payment {subject_status}</h2>
                <p>Hello,</p>
                <p>Your manual payment for Order <strong>#{order_id}</strong> has been <strong style="color: {color}">{subject_status}</strong>.</p>
                <p>{message_text}</p>
                <br>
                <p>Happy Learning!</p>
                <p>The CodeMaster Team</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP Server
        if settings.EMAIL_PORT == 465:
            # Use SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            # Use SMTP with STARTTLS for port 587 and others
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Order status email sent to {user_email} for Order #{order_id}")
        return True
    except Exception as e:
        logging.error(f"Failed to send order status email: {e}")
        return False
