#!/usr/bin/env python3
"""
Quick test for API endpoints
"""
import subprocess
import time

# Wait for server to start
time.sleep(2)

# Test login
print("Testing Login...")
result = subprocess.run([
    "curl", "-X", "POST",
    "http://localhost:8000/api/v1/auth/login",
    "-H", "Content-Type: application/json",
    "-d", '{"email":"john@example.com","password":"password123"}'
], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
