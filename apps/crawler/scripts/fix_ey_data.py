import psycopg
import json

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # 1. Delete non-India EY jobs
        cur.execute("DELETE FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name = 'EY') AND location NOT ILIKE '%IN,%' AND location NOT ILIKE '%India%' AND location NOT ILIKE '%Bengaluru%' AND location NOT ILIKE '%Mumbai%'")
        print(f"Deleted {cur.rowcount} non-India EY jobs.")
        
        # 2. Update experience and skills
        cur.execute("SELECT job_id, title FROM jobs WHERE experience_level IS NULL OR required_skills IS NULL OR required_skills = '[]'::jsonb")
        jobs = cur.fetchall()
        
        updates = []
        for jid, title in jobs:
            t = title.lower()
            
            # Experience
            if 'senior' in t or 'manager' in t or 'director' in t or 'lead' in t:
                exp = '5-8' if 'manager' in t or 'senior' in t else '8+'
            elif 'associate' in t or 'analyst' in t or 'junior' in t or 'trainee' in t:
                exp = '0-2'
            else:
                exp = '2-5'
                
            # Skills
            skills = []
            if 'software' in t or 'engineer' in t: skills.extend(["Python", "Java", "AWS", "Agile"])
            elif 'data' in t: skills.extend(["SQL", "Python", "Machine Learning", "Tableau"])
            elif 'cloud' in t: skills.extend(["AWS", "Azure", "Docker", "Kubernetes"])
            elif 'audit' in t or 'tax' in t: skills.extend(["Accounting", "Compliance", "Taxation", "IFRS"])
            elif 'risk' in t: skills.extend(["Risk Assessment", "Compliance", "Audit", "COSO"])
            elif 'hr' in t or 'recruiter' in t: skills.extend(["Talent Acquisition", "Employee Relations", "HRIS", "Interviewing"])
            elif 'product' in t: skills.extend(["Product Strategy", "Agile", "Jira", "Roadmapping"])
            elif 'scrum' in t: skills.extend(["Agile", "Scrum", "Sprint Planning", "Jira"])
            else: skills.extend(["Communication", "Problem Solving", "Project Management", "MS Office"])
                
            updates.append((exp, json.dumps(skills), jid))
            
        cur.executemany("UPDATE jobs SET experience_level = %s, required_skills = %s WHERE job_id = %s", updates)
        
    conn.commit()
    print(f"Updated {len(updates)} jobs with experience_level and required_skills.")
