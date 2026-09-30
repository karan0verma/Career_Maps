import requests
import uuid
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.db.session import SessionLocal
from src.models.user import User

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_result(name, passed, msg=""):
    status = "PASS" if passed else "FAIL"
    print(f"{status} | {name} {msg}")
    if not passed:
        global ALL_PASSED
        ALL_PASSED = False

ALL_PASSED = True
report_lines = ["# API Test Report\n"]

def test_auth():
    print("\n--- Testing Authentication ---")
    
    # 1. Register User
    username = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123"
    
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": username,
        "password": password,
        "full_name": "Test User"
    })
    print_result("Register User", res.status_code == 200, res.text)
    user_id = res.json().get("user_id") if res.status_code == 200 else None
    
    # 2. Register Admin
    admin_name = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": admin_name,
        "password": password,
        "full_name": "Test Admin"
    })
    print_result("Register Admin", res.status_code == 200, res.text)
    
    # Promote admin in DB
    db = SessionLocal()
    u = db.query(User).filter(User.email == admin_name).first()
    if u:
        u.role = 'ADMIN'
        db.commit()
    db.close()
    
    # 3. Login User
    res = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    print_result("Login User", res.status_code == 200)
    user_token = res.json().get("access_token") if res.status_code == 200 else None
    
    # 4. Login Admin
    res = requests.post(f"{BASE_URL}/auth/login", data={
        "username": admin_name,
        "password": password
    })
    print_result("Login Admin", res.status_code == 200)
    admin_token = res.json().get("access_token") if res.status_code == 200 else None
    
    return user_token, admin_token, user_id

def test_rbac(user_token, admin_token):
    print("\n--- Testing RBAC ---")
    headers_user = {"Authorization": f"Bearer {user_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    res = requests.get(f"{BASE_URL}/admin/companies", headers=headers_user)
    print_result("User accessing Admin (Unauthorized)", res.status_code == 403 or res.status_code == 401)
    
    res = requests.get(f"{BASE_URL}/admin/companies", headers=headers_admin)
    print_result("Admin accessing Admin (Authorized)", res.status_code == 200)

def test_companies_admin(admin_token):
    print("\n--- Testing Admin Companies CRUD ---")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create
    unique = uuid.uuid4().hex[:4]
    res = requests.post(f"{BASE_URL}/admin/companies", headers=headers, json={
        "official_name": f"Test Company {unique}",
        "display_name": f"TestCo {unique}",
        "website": f"testco{unique}.com",
        "career_url": f"https://testco{unique}.com/careers",
        "is_active": True
    })
    print_result("Create Company", res.status_code == 200, res.text)
    company_id = res.json().get("company_id") if res.status_code == 200 else None
    
    # Update
    res = requests.put(f"{BASE_URL}/admin/companies/{company_id}", headers=headers, json={
        "display_name": f"Updated TestCo {unique}"
    })
    print_result("Update Company", res.status_code == 200 and res.json().get("display_name") == f"Updated TestCo {unique}")
    
    # Soft Delete
    res = requests.delete(f"{BASE_URL}/admin/companies/{company_id}", headers=headers)
    print_result("Delete Company", res.status_code == 200 and res.json().get("is_deleted") == True)
    
    return company_id

def test_csv_import(admin_token):
    print("\n--- Testing CSV Import ---")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    csv_data = """Company Name,Domain,Career URL
ImportCo,importco.com,https://importco.com/careers
ImportCo2,importco2.com,https://importco2.com/careers"""
    
    res = requests.post(
        f"{BASE_URL}/admin/companies/import", 
        headers=headers,
        files={"file": ("test.csv", csv_data, "text/csv")}
    )
    print_result("CSV Import", res.status_code == 200, res.text)

def test_crawler(admin_token):
    print("\n--- Testing Crawl ---")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Insert coinbase
    res = requests.post(f"{BASE_URL}/admin/companies", headers=headers, json={
        "official_name": "Coinbase",
        "display_name": "Coinbase",
        "website": "coinbase.com",
        "is_active": True
    })
    if res.status_code == 400: # might already exist
        res = requests.get(f"{BASE_URL}/admin/companies", headers=headers)
        coinbase = next((c for c in res.json() if c["website"] == "coinbase.com"), None)
        company_id = coinbase["company_id"]
    else:
        company_id = res.json().get("company_id")
        
    # Trigger crawl
    res = requests.post(f"{BASE_URL}/admin/companies/{company_id}/crawl", headers=headers, json={"trigger_type": "MANUAL"})
    print_result("Single Crawl (Coinbase)", res.status_code == 200, res.text)
    
    if res.status_code == 200:
        crawl_id = res.json().get("crawl_id")
        jobs_added = res.json().get("jobs_added")
        jobs_found = res.json().get("jobs_found")
        print_result("Jobs extracted", jobs_found > 0, f"Added: {jobs_added}, Found: {jobs_found}")
        
        # Retry Crawl
        res = requests.post(f"{BASE_URL}/admin/crawls/{crawl_id}/retry", headers=headers)
        print_result("Retry Crawl", res.status_code == 200, res.text)
    
    # Batch crawl
    res = requests.post(f"{BASE_URL}/admin/crawls/batch", headers=headers, json={"company_ids": [company_id]})
    print_result("Batch Crawl", res.status_code == 200, res.text)

def test_public_and_user_features(user_token):
    print("\n--- Testing Public & User Features ---")
    headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}
    
    # Get Companies
    res = requests.get(f"{BASE_URL}/companies")
    print_result("List Companies (Public)", res.status_code == 200 and isinstance(res.json(), list))
    
    # Job Search
    res = requests.get(f"{BASE_URL}/jobs", params={"q": "engineer", "limit": 10}, headers=headers)
    print_result("Job Search", res.status_code == 200 and isinstance(res.json(), list), f"Found {len(res.json()) if res.status_code == 200 else 0}")
    jobs = res.json() if res.status_code == 200 else []
    
    if jobs:
        job_id = jobs[0]["job_id"]
        
        # Get Job Details (logs view)
        res = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        print_result("Job Details", res.status_code == 200)
        
        # Save Job
        res = requests.post(f"{BASE_URL}/users/me/saved_jobs", params={"job_id": job_id}, headers=headers)
        print_result("Save Job", res.status_code == 200, res.text)
        
        # List Saved Jobs
        res = requests.get(f"{BASE_URL}/users/me/saved_jobs", headers=headers)
        print_result("List Saved Jobs", res.status_code == 200 and len(res.json()) > 0)
        
        # Delete Saved Job
        res = requests.delete(f"{BASE_URL}/users/me/saved_jobs/{job_id}", headers=headers)
        print_result("Unsave Job", res.status_code == 200)
        
        # Viewed Jobs
        res = requests.get(f"{BASE_URL}/users/me/viewed_jobs", headers=headers)
        print_result("List Viewed Jobs", res.status_code == 200 and len(res.json()) > 0)
        
        # Search History
        res = requests.get(f"{BASE_URL}/users/me/search_history", headers=headers)
        print_result("List Search History", res.status_code == 200 and len(res.json()) > 0)

if __name__ == "__main__":
    try:
        user_token, admin_token, user_id = test_auth()
        if user_token and admin_token:
            test_rbac(user_token, admin_token)
            test_companies_admin(admin_token)
            test_csv_import(admin_token)
            test_crawler(admin_token)
            test_public_and_user_features(user_token)
            
            # Error / Invalid requests
            print("\n--- Testing Error Handling ---")
            res = requests.get(f"{BASE_URL}/jobs/not-a-uuid")
            print_result("Invalid UUID Format", res.status_code == 422)
            
            res = requests.get(f"{BASE_URL}/jobs/{uuid.uuid4()}")
            print_result("Non-existent Job", res.status_code == 404)
            
    except Exception as e:
        print_result("Test execution", False, str(e))
        
    print(f"\nOVERALL STATUS: {'PASSED' if ALL_PASSED else 'FAILED'}")
