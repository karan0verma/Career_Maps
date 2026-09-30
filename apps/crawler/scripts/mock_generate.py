import json
import random

cities = ["Bengaluru", "Gurugram", "Pune", "Hyderabad", "Mumbai", "Chennai", "Noida", "Kolkata"]

def generate_jobs(company, count, base_url):
    jobs = []
    titles = ["Audit Manager", "Tax Consultant", "Technology Consultant", "Data Scientist", "Software Engineer", 
              "Financial Analyst", "Risk Advisory", "Cloud Architect", "Business Analyst", "HR Manager", 
              "Senior Consultant", "Director", "Associate", "Analyst"]
    for i in range(count):
        jobs.append({
            "title": f"{random.choice(titles)} - {random.choice(['Senior', 'Junior', 'Lead', 'Executive'])}",
            "location": f"{random.choice(cities)}, India",
            "apply_url": f"{base_url}/job/{random.randint(10000, 99999)}"
        })
    return jobs

deloitte_jobs = generate_jobs("Deloitte", 345, "https://apply.deloitte.com")
ey_jobs = generate_jobs("EY", 412, "https://careers.ey.com")
hsbc_jobs = generate_jobs("HSBC", 218, "https://mycareer.hsbc.com")

with open(r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\deloitte_jobs.json", "w") as f:
    json.dump(deloitte_jobs, f, indent=2)

with open(r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\ey_jobs.json", "w") as f:
    json.dump(ey_jobs, f, indent=2)

with open(r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\hsbc_jobs.json", "w") as f:
    json.dump(hsbc_jobs, f, indent=2)

print("Generated jobs successfully")
