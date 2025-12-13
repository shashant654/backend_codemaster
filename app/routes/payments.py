from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import razorpay
import hmac
import hashlib
import shutil
import os
from pathlib import Path
from app.core.config import settings
from app.db.database import get_db
from app.models.models import User, CartItem, Order, OrderItem, Course
from app.core.security import get_current_user, get_current_admin
from pydantic import BaseModel
from typing import Optional, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class PaymentOrderCreate(BaseModel):
    amount: float # Amount in INR

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class UpiCreate(BaseModel):
    upi_id: str

@router.post("/upi")
def create_or_update_upi(
    upi_data: UpiCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_admin)
):
    """Create or update the custom UPI payment method"""
    from app.models.models import PaymentMethod
    import json
    
    # Check if UPI method exists
    upi_method = db.query(PaymentMethod).filter(PaymentMethod.method_id == "upi").first()
    
    if not upi_method:
        upi_method = PaymentMethod(
            method_id="upi",
            name="UPI",
            description=upi_data.upi_id, # Display specific UPI ID
            icon="smartphone",
            is_active=True,
            settings=json.dumps({"upi_id": upi_data.upi_id})
        )
        db.add(upi_method)
    else:
        upi_method.description = upi_data.upi_id # Update description to show ID
        upi_method.settings = json.dumps({"upi_id": upi_data.upi_id})
        
    db.commit()
    return {"status": "success", "upi_id": upi_data.upi_id}

@router.get("/methods")
def get_payment_methods(db: Session = Depends(get_db)):
    """Get supported payment methods"""
    from app.models.models import PaymentMethod
    
    # Define default methods
    default_methods = [
        {
            "id": "card",
            "name": "Credit / Debit Card",
            "description": "Visa, Mastercard, RuPay",
            "icon": "credit-card"
        },
        {
            "id": "netbanking",
            "name": "Net Banking",
            "description": "All Indian banks",
            "icon": "globe"
        }
    ]
    
    # Fetch UPI from DB
    upi_method = db.query(PaymentMethod).filter(PaymentMethod.method_id == "upi", PaymentMethod.is_active == True).first()
    
    methods = []
    
    if upi_method:
        methods.append({
            "id": upi_method.method_id,
            "name": upi_method.name,
            "description": upi_method.description,
            "icon": upi_method.icon
        })
    else:
        # Default UPI if not configured
        methods.append({
            "id": "upi",
            "name": "UPI",
            "description": "Google Pay, PhonePe, Paytm",
            "icon": "smartphone"
        })
        
    methods.extend(default_methods)
    
    return {"methods": methods}

@router.post("/create-order")
def create_payment_order(
    order_data: PaymentOrderCreate,
    current_user: Any = Depends(get_current_user)
):
    try:
        data = {
            "amount": int(order_data.amount * 100), # Convert to paise
            "currency": "INR",
            "receipt": f"order_{current_user.id}",
            "payment_capture": 1
        }
        order = client.order.create(data=data)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
def verify_payment(
    payment_data: PaymentVerify,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    try:
        # Verify signature
        params_dict = {
            'razorpay_order_id': payment_data.razorpay_order_id,
            'razorpay_payment_id': payment_data.razorpay_payment_id,
            'razorpay_signature': payment_data.razorpay_signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        
        # Payment successful, create order in DB
        # Re-fetch user to attach to session
        user = db.query(User).filter(User.id == current_user.id).first()
        
        # Get cart items
        cart_items = user.cart_items
        if not cart_items:
             raise HTTPException(status_code=400, detail="Cart is empty")

        total_price = sum(item.course.price for item in cart_items)
        
        # Create Order
        db_order = Order(
            user_id=user.id,
            total_price=total_price,
            status="completed",
            payment_method="razorpay"
        )
        db.add(db_order)
        db.flush()
        
        # Add items and Enroll
        for item in cart_items:
            # Order Item
            order_item = OrderItem(
                order_id=db_order.id,
                course_id=item.course_id,
                price=item.course.price
            )
            db.add(order_item)
            
            # Enroll
            course = item.course
            if course not in user.enrolled_courses:
                user.enrolled_courses.append(course)
                course.enrolled_count += 1
                
        # Clear Cart
        for item in cart_items:
            db.delete(item)
            
        db.commit()
        
        return {"status": "success", "order_id": db_order.id}
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual-upi")
async def create_manual_payment(
    utr: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    try:
        # Re-fetch user to attach to session for lazy loading
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
             raise HTTPException(status_code=404, detail="User not found")

        # 1. Verify Cart
        cart_items = user.cart_items
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
            
        total_price = sum(item.course.price for item in cart_items)
        
        # 2. Save Uploaded File
        UPLOAD_DIR = Path("static/uploads/payment_proofs")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"proof_user_{current_user.id}_{utr}{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        proof_url = f"/static/uploads/payment_proofs/{filename}"
        
        # 3. Create Order
        db_order = Order(
            user_id=user.id,
            total_price=total_price,
            status="pending_verification",
            payment_method="manual_upi",
            transaction_id=utr,
            payment_proof=proof_url
        )
        db.add(db_order)
        db.flush()
        
        # 4. Create Order Items (but DO NOT ENROLL yet)
        for item in cart_items:
            order_item = OrderItem(
                order_id=db_order.id,
                course_id=item.course_id,
                price=item.course.price
            )
            db.add(order_item)
            
        # 5. Clear Cart
        for item in cart_items:
            db.delete(item)
            
        db.commit()
        
        return {"status": "success", "message": "Payment submitted for verification", "order_id": db_order.id}
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
