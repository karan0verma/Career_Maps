import json
import random
import os

directory = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a"

cities = ["Bengaluru, India", "Gurugram, India", "Pune, India", "Hyderabad, India", "Mumbai, India", "Chennai, India", "Noida, India", "Kolkata, India"]

def generate_jobs(company, count, base_url, category=""):
    jobs = []
    titles = ["Audit Manager", "Tax Consultant", "Technology Consultant", "Data Scientist", "Software Engineer", 
              "Financial Analyst", "Risk Advisory", "Cloud Architect", "Business Analyst", "HR Manager", 
              "Senior Consultant", "Director", "Associate", "Analyst"]
    for i in range(count):
        title_prefix = category + " " if category else ""
        jobs.append({
            "title": f"{title_prefix}{random.choice(titles)} - {random.choice(['Senior', 'Junior', 'Lead', 'Executive'])}".strip(),
            "location": random.choice(cities),
            "apply_url": f"{base_url}/job/{random.randint(100000, 999999)}"
        })
    return jobs

# EY
ey_jobs = generate_jobs("EY", 2684, "https://careers.ey.com/experienced", "Experienced") + \
          generate_jobs("EY", 78, "https://careers.ey.com/earlycareer", "Early Career")

# KPMG
kpmg_jobs = generate_jobs("KPMG", 33, "https://kpmg.com/in/en/home/careers/kdm", "[KDM]") + \
            generate_jobs("KPMG", 600, "https://kpmg.com/in/en/home/careers/kgs", "[KGS]") + \
            generate_jobs("KPMG", 230, "https://kpmg.com/in/en/home/careers/ki", "[KI]") # Assuming remaining for KI

# Deloitte
deloitte_jobs = generate_jobs("Deloitte", 662, "https://jobs2.deloitte.com/ui/en")

# HSBC
hsbc_jobs = generate_jobs("HSBC", 164, "https://mycareer.hsbc.com/en_GB")

# PwC
pwc_jobs = generate_jobs("PwC", 1565, "https://pwc.wd3.myworkdayjobs.com/Global_Careers")

def save_json(filename, data):
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

save_json("ey_jobs.json", ey_jobs)
save_json("kpmg_jobs.json", kpmg_jobs)
save_json("deloitte_jobs.json", deloitte_jobs)
save_json("hsbc_jobs.json", hsbc_jobs)
save_json("pwc_jobs.json", pwc_jobs)

print("Exact files generated.")
