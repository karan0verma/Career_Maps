import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.db.session import SessionLocal
from src.models.job import Job

# Mapping common Indian cities to their states
CITY_TO_STATE = {
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "gurugram": "Haryana",
    "gurgaon": "Haryana",
    "faridabad": "Haryana",
    "noida": "Uttar Pradesh",
    "greater noida": "Uttar Pradesh",
    "ghaziabad": "Uttar Pradesh",
    "lucknow": "Uttar Pradesh",
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "hyderabad": "Telangana",
    "kolkata": "West Bengal",
    "ahmedabad": "Gujarat",
    "gandhinagar": "Gujarat",
    "surat": "Gujarat",
    "kochi": "Kerala",
    "trivandrum": "Kerala",
    "thiruvananthapuram": "Kerala",
    "jaipur": "Rajasthan",
    "jodhpur": "Rajasthan",
    "chandigarh": "Chandigarh",
    "indore": "Madhya Pradesh",
    "bhopal": "Madhya Pradesh",
    "bhubaneswar": "Odisha",
    "dehradun": "Uttarakhand",
    "patna": "Bihar",
    "ranchi": "Jharkhand",
    "guwahati": "Assam"
}

def enrich_jobs():
    db = SessionLocal()
    jobs = db.query(Job).filter(Job.is_active == True).all()
    
    updated_count = 0
    
    for job in jobs:
        changed = False
        title = (job.title or "").lower()
        desc = (job.description or "").lower()
        loc = (job.location or "").lower()
        
        combined_text = f"{title} {loc}"
        
        # 1. Work Mode Heuristics
        if not job.work_mode:
            if "remote" in combined_text or "work from home" in combined_text or "wfh" in combined_text:
                job.work_mode = "Remote"
                changed = True
            elif "hybrid" in combined_text:
                job.work_mode = "Hybrid"
                changed = True
            elif "on-site" in combined_text or "onsite" in combined_text or "in-office" in combined_text:
                job.work_mode = "On-site"
                changed = True
            else:
                job.work_mode = "On-site"  # Default assumption for Indian IT jobs unless specified
                changed = True

        # 2. Employment Type Heuristics
        if not job.employment_type or job.employment_type.lower() not in ["intern", "full-time", "contract"]:
            if "intern" in title or "internship" in title or "trainee" in title:
                job.employment_type = "Intern"
                changed = True
            elif "contract" in title or "freelance" in title:
                job.employment_type = "Contract"
                changed = True
            elif "part-time" in title or "part time" in title:
                job.employment_type = "Part-time"
                changed = True
            else:
                job.employment_type = "Full-time"
                changed = True
                
        # 3. Experience / Level Heuristics (Optional mapping to department or a new field, we will map to department if empty)
        if not job.department:
            if "fresher" in title or "graduate" in title or "entry level" in title or "junior" in title or "jr" in title:
                job.department = "Entry-level"
                changed = True
            elif "senior" in title or "sr" in title or "lead" in title or "principal" in title or "manager" in title or "director" in title or "head" in title or "vp" in title:
                job.department = "Experienced"
                changed = True
            else:
                job.department = "Mid-level"
                changed = True

        # 4. State Extraction
        if not job.state:
            for city_key, state_val in CITY_TO_STATE.items():
                if city_key in loc:
                    job.state = state_val
                    changed = True
                    # Also standardize city if missing
                    if not job.city:
                        job.city = city_key.title()
                    break

        if changed:
            updated_count += 1
            
    db.commit()
    print(f"Enriched metadata for {updated_count} jobs out of {len(jobs)}.")

if __name__ == "__main__":
    enrich_jobs()
