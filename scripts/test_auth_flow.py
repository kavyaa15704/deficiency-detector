"""
Test the full register -> login -> authenticated predict flow directly
against the running API, with no browser/Swagger involved.

Make sure the server is running first:  uvicorn app.main:app --reload
Then, in a second terminal:              python scripts/test_auth_flow.py
"""
import random

import requests

BASE_URL = "http://127.0.0.1:8000"
USERNAME = f"testuser{random.randint(1000, 9999)}"  # fresh username each run
PASSWORD = "testpass123"
EMAIL = f"{USERNAME}@example.com"


def main():
    print(f"Using test user: {USERNAME}\n")

    # 1. Register
    r = requests.post(f"{BASE_URL}/register", json={
        "username": USERNAME, "email": EMAIL, "password": PASSWORD,
    })
    print(f"[1] POST /register -> {r.status_code}")
    print(r.json(), "\n")
    assert r.status_code == 201, "Registration failed - stop here and check the server logs."

    # 2. Login (form data, not JSON - this endpoint uses OAuth2PasswordRequestForm)
    r = requests.post(f"{BASE_URL}/login", data={
        "username": USERNAME, "password": PASSWORD,
    })
    print(f"[2] POST /login -> {r.status_code}")
    print(r.json(), "\n")
    assert r.status_code == 200, "Login failed - stop here and check the server logs."
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Predict WITHOUT a token - should be rejected
    r = requests.post(f"{BASE_URL}/predict", json={
        "symptoms": ["fatigue", "pale_skin", "dizziness", "cold_hands_feet"],
    })
    print(f"[3] POST /predict (no token) -> {r.status_code} (expect 401)")
    print(r.json(), "\n")

    # 4. Predict WITH a token - should succeed
    r = requests.post(f"{BASE_URL}/predict", json={
        "symptoms": ["fatigue", "pale_skin", "dizziness", "cold_hands_feet"],
    }, headers=headers)
    print(f"[4] POST /predict (with token) -> {r.status_code} (expect 200)")
    result = r.json()
    print(f"    Top prediction: {result['predictions'][0]['nutrient']} "
          f"({result['predictions'][0]['confidence']:.1%})\n")

    # 5. Recent predictions - should show this one
    r = requests.get(f"{BASE_URL}/predictions/recent", headers=headers)
    print(f"[5] GET /predictions/recent -> {r.status_code}")
    print(f"    {len(r.json()['predictions'])} prediction(s) found for this user\n")

    print("All checks passed." if r.status_code == 200 else "Something's off - see above.")


if __name__ == "__main__":
    main()
