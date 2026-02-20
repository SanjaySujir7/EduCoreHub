import requests

BASE_URL = "http://127.0.0.1:8000"  # Change if your server runs on different port

url = f"{BASE_URL}/register/student"

# Test data
student_data = {
    "full_name": "Sanjay",
    "email": "sanjay@test.com",
    "password": "password123",
    "usn": "1RV21CS001",
    "semester_id": 1
}

try:
    response = requests.post(url, json=student_data)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.ConnectionError:
    print("❌ Server is not running. Start FastAPI first!")