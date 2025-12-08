from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import Order, OrderItem, CartItem, Course, User
from app.schemas.schemas import OrderCreate, OrderResponse
from app.core.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_from_cart(
    payment_method: Optional[str] = "credit_card",
    coupon_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create order from cart items"""
    # Get cart items
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    courses_to_order = []
    subtotal = 0.0
    
    for item in cart_items:
        course = item.course
        
        # Check if already enrolled
        if course in current_user.enrolled_courses:
            # Remove from cart and skip
            db.delete(item)
            continue
            
        courses_to_order.append(course)
        subtotal += course.price
    
    if not courses_to_order:
        raise HTTPException(
            status_code=400,
            detail="All courses in cart are already enrolled"
        )
    
    # Apply discount if coupon provided
    discount = 0.0
    if coupon_code:
        valid_coupons = {
            "SAVE20": 20,
            "SAVE10": 10,
            "WELCOME": 15,
            "STUDENT50": 50
        }
        if coupon_code.upper() in valid_coupons:
            discount_percent = valid_coupons[coupon_code.upper()]
            discount = (subtotal * discount_percent) / 100
    
    total_price = subtotal - discount
    
    # Create order
    db_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status="completed",
        payment_method=payment_method
    )
    db.add(db_order)
    db.flush()
    
    # Create order items and enroll user
    for course in courses_to_order:
        # Create order item
        order_item = OrderItem(
            order_id=db_order.id,
            course_id=course.id,
            price=course.price
        )
        db.add(order_item)
        
        # Enroll user in course
        if course not in current_user.enrolled_courses:
            current_user.enrolled_courses.append(course)
            course.enrolled_count += 1
    
    # Clear cart
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order from course IDs"""
    courses_to_order = []
    total_price = 0.0
    
    # Validate courses
    if order_data.course_ids:
        for course_id in order_data.course_ids:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=404,
                    detail=f"Course {course_id} not found"
                )
            
            # Check if already enrolled
            if course in current_user.enrolled_courses:
                continue
                
            courses_to_order.append(course)
            total_price += course.price
    else:
        raise HTTPException(status_code=400, detail="No courses provided")
    
    if not courses_to_order:
        raise HTTPException(
            status_code=400,
            detail="Already enrolled in all specified courses"
        )
    
    # Create order
    db_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status="completed",
        payment_method=order_data.payment_method or "credit_card"
    )
    db.add(db_order)
    db.flush()
    
    # Create order items and enroll
    for course in courses_to_order:
        order_item = OrderItem(
            order_id=db_order.id,
            course_id=course.id,
            price=course.price
        )
        db.add(order_item)
        
        if course not in current_user.enrolled_courses:
            current_user.enrolled_courses.append(course)
            course.enrolled_count += 1
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's order history"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own orders"
        )
    
    return order

@router.get("/latest/details")
def get_latest_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's latest order"""
    order = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="No orders found")
    
    return order

@router.post("/refund/{order_id}")
def request_refund(
    order_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request refund for an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only refund your own orders"
        )
    
    if order.status == "refunded":
        raise HTTPException(status_code=400, detail="Order already refunded")
    
    # Check if within refund period (30 days for demo)
    days_since_order = (datetime.utcnow() - order.created_at).days
    if days_since_order > 30:
        raise HTTPException(
            status_code=400,
            detail="Refund period expired (30 days)"
        )
    
    # Update order status
    order.status = "refunded"
    order.updated_at = datetime.utcnow()
    
    # Unenroll from courses
    for item in order.order_items:
        course = item.course
        if course in current_user.enrolled_courses:
            current_user.enrolled_courses.remove(course)
            course.enrolled_count -= 1
    
    db.commit()
    
    return {
        "message": "Refund processed successfully",
        "order_id": order_id,
        "refund_amount": order.total_price
    }