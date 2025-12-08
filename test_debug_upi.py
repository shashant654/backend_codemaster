import requests
import os

BASE_URL = "http://localhost:8001/api/v1"

def debug_upi():
    # 1. Login
    print("Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "shashantshekhar10@gmail.com",
        "password": "password123" 
    })
    
    # If login fails, try to register
    if login_resp.status_code != 200:
        print("Login failed, trying to register...")
        reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test_upi_user_v6@example.com", 
            "password": "password123",
            "name": "Test User"
        })
        if reg_resp.status_code == 200:
             login_resp = requests.post(f"{BASE_URL}/auth/login", data={
                "username": "test_upi_user_v6@example.com",
                "password": "password123" 
            })
    
    if login_resp.status_code != 200:
        print(f"Authentication failed: {login_resp.text}")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully.")

    # 2. Add course to cart (we need a course first)
    # Get courses
    courses_resp = requests.get(f"{BASE_URL}/courses")
    courses = courses_resp.json()
    if not courses:
        print("No courses found. Cannot test.")
        return
        
    course_id = courses[0]["id"]
    print(f"Adding course {course_id} to cart...")
    requests.post(f"{BASE_URL}/cart/add/{course_id}", headers=headers)

    # 3. Submit Manual UPI
    print("Submitting Manual UPI payment...")
    
    # Create a dummy image
    with open("dummy_proof.png", "wb") as f:
        f.write(os.urandom(1024))
        
    files = {'file': ('dummy_proof.png', open('dummy_proof.png', 'rb'), 'image/png')}
    data = {'utr': '123456789012'}
    
    resp = requests.post(f"{BASE_URL}/payments/manual-upi", headers=headers, files=files, data=data)
    
    print(f"Status Code: {resp.status_code}")
    print("Response Body:")
    print(resp.text)

if __name__ == "__main__":
    debug_upi()
