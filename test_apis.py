#!/usr/bin/env python3
"""
Test script for the new API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"
TOKEN = None

def test_login():
    """Test login endpoint"""
    global TOKEN
    print("\n=== Testing Login ===")
    data = {
        "email": "john@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        TOKEN = result.get("access_token")
        print(f"Token: {TOKEN[:20]}...")
        print("✓ Login successful")
        return True
    else:
        print(f"✗ Login failed: {response.text}")
        return False

def test_create_review():
    """Test creating a review"""
    print("\n=== Testing Create Review ===")
    if not TOKEN:
        print("✗ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "course_id": 1,
        "rating": 5,
        "comment": "Excellent course! Learned a lot."
    }
    response = requests.post(f"{BASE_URL}/reviews/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"Review created: {json.dumps(result, indent=2)}")
        print("✓ Review creation successful")
        return True
    else:
        print(f"✗ Review creation failed: {response.text}")
        return False

def test_list_reviews():
    """Test listing reviews for a course"""
    print("\n=== Testing List Reviews ===")
    response = requests.get(f"{BASE_URL}/reviews/?course_id=1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        reviews = response.json()
        print(f"Found {len(reviews)} reviews")
        print(f"Reviews: {json.dumps(reviews, indent=2)}")
        print("✓ List reviews successful")
        return True
    else:
        print(f"✗ List reviews failed: {response.text}")
        return False

def test_create_order():
    """Test creating an order"""
    print("\n=== Testing Create Order ===")
    if not TOKEN:
        print("✗ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "course_ids": [1, 2],
        "payment_method": "credit_card"
    }
    response = requests.post(f"{BASE_URL}/orders/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"Order created: {json.dumps(result, indent=2)}")
        print("✓ Order creation successful")
        return True
    else:
        print(f"✗ Order creation failed: {response.text}")
        return False

def test_list_orders():
    """Test listing orders"""
    print("\n=== Testing List Orders ===")
    if not TOKEN:
        print("✗ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/orders/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"Found {len(orders)} orders")
        print(f"Orders: {json.dumps(orders, indent=2)}")
        print("✓ List orders successful")
        return True
    else:
        print(f"✗ List orders failed: {response.text}")
        return False

def test_update_profile():
    """Test updating user profile"""
    print("\n=== Testing Update Profile ===")
    if not TOKEN:
        print("✗ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "name": "John Doe Updated",
        "bio": "Updated bio"
    }
    response = requests.put(f"{BASE_URL}/users/profile/update", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Profile updated: {json.dumps(result, indent=2)}")
        print("✓ Profile update successful")
        return True
    else:
        print(f"✗ Profile update failed: {response.text}")
        return False

def test_change_password():
    """Test changing password"""
    print("\n=== Testing Change Password ===")
    if not TOKEN:
        print("✗ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "current_password": "password123",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }
    response = requests.post(f"{BASE_URL}/users/password/change", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        print("✓ Password change successful")
        return True
    else:
        print(f"✗ Password change failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing CodeMaster API Endpoints")
    print("=" * 50)
    
    tests = [
        test_login,
        test_create_review,
        test_list_reviews,
        test_create_order,
        test_list_orders,
        test_update_profile,
        # test_change_password,  # Uncomment to test
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

if __name__ == "__main__":
    main()
