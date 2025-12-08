from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import User, CartItem, Course
from app.schemas.schemas import CartItemResponse, CartItemBase
from app.core.security import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=List[CartItemResponse])
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart items"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return cart_items

@router.post("/add", response_model=CartItemResponse)
def add_to_cart(
    cart_item: CartItemBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add course to cart"""
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.course_id == cart_item.course_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Course already in cart")
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == cart_item.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create new cart item
    new_item = CartItem(user_id=current_user.id, course_id=cart_item.course_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}

@router.get("/count")
def get_cart_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of items in cart"""
    count = db.query(CartItem).filter(CartItem.user_id == current_user.id).count()
    return {"count": count}
