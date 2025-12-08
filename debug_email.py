from app.core.email import send_payment_notification
from app.core.config import settings

print(f"Testing email to {settings.EMAIL_HOST_USER}")
try:
    success = send_payment_notification(
        order_id=9999,
        amount=1.0,
        user_email="test@example.com",
        proof_url="http://test.com/image.png",
        utr="TEST_UTR_123"
    )
    if success:
        print("Email sent successfully!")
    else:
        print("Email failed (check logs/output above) - but function caught it.")
except Exception as e:
    print(f"CRITICAL FAIL: {e}")
