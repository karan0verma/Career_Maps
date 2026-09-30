import requests
import json

url = 'https://public.zwayam.com/jobs/search'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Origin': 'https://careers.coforge.com',
    'Referer': 'https://careers.coforge.com/coforge/'
}

all_raw_jobs = []
start = 0

while True:
    d = {
        'filterCri': json.dumps({
            'paginationStartNo': start,
            'selectedCall': 'sort',
            'sortCriteria': {
                'name': 'modifiedDate',
                'isAscending': False
            },
            'anyOfTheseWords': ''
        }),
        'domain': 'careers.coforge.com',
        'companyId': 'MTUxNzM='
    }
    r = requests.post(url, headers=headers, data=d)
    if r.status_code != 200:
        break
    items = r.json().get('data', {}).get('data', [])
    if not items:
        break
    all_raw_jobs.extend(items)
    if len(items) < 10:
        break
    start += len(items)

print("=" * 70)
print(f"COFORGE JOB AUDIT REPORT: {len(all_raw_jobs)} DISCOVERED JOBS")
print("=" * 70)

valid_jobs = []
invalid_jobs = []
duplicate_jobs = []
seen_ids = set()
seen_urls = set()

location_breakdown = {}
experience_breakdown = {}

for item in all_raw_jobs:
    j = item.get('_source', item)
    job_id = str(j.get('id') or item.get('_id'))
    title = j.get('jobTitle') or j.get('designation') or j.get('roles')
    slug = j.get('jobUrl') or f"job-{job_id}"
    apply_url = f"https://careers.coforge.com/coforge/jobview/{slug}?id={job_id}"
    
    # Location
    loc_records = j.get('jobLocationRecord', [])
    if loc_records and isinstance(loc_records, list) and len(loc_records) > 0:
        city = loc_records[0].get('city') or j.get('location') or 'Global'
        country = loc_records[0].get('country') or 'India'
        state = loc_records[0].get('state')
        location = loc_records[0].get('formattedLocation') or f"{city}, {country}"
    else:
        city = j.get('location') or 'Global'
        country = 'India'
        location = f"{city}, {country}"
        
    experience = j.get('yrsOfExperience') or (f"{j.get('minYrsOfExperience', '')} Years" if j.get('minYrsOfExperience') else None)
    skills = j.get('mandatorySkills') or []
    if not skills and j.get('jdSkillsKnownList'):
        skills = j.get('jdSkillsKnownList')[:5]
        
    desc = j.get('shortDescription') or ""
    
    # Check duplicate
    if job_id in seen_ids or apply_url in seen_urls:
        duplicate_jobs.append(j)
        continue
    seen_ids.add(job_id)
    seen_urls.add(apply_url)
    
    # Check valid
    if not title or len(title.strip()) < 2:
        invalid_jobs.append((j, "Missing title"))
        continue
        
    if not desc or len(desc.strip()) < 10:
        invalid_jobs.append((j, "Missing description"))
        continue
        
    valid_jobs.append({
        "job_id": job_id,
        "title": title.strip(),
        "location": location,
        "city": city,
        "country": country,
        "experience": experience,
        "skills": skills,
        "apply_url": apply_url,
        "desc_length": len(desc),
        "desc_preview": desc[:150]
    })
    
    location_breakdown[location] = location_breakdown.get(location, 0) + 1
    if experience:
        experience_breakdown[experience] = experience_breakdown.get(experience, 0) + 1

print(f"1. Total Jobs Discovered : {len(all_raw_jobs)}")
print(f"2. Valid Jobs for Import : {len(valid_jobs)}")
print(f"3. Invalid / Incomplete  : {len(invalid_jobs)}")
print(f"4. Duplicate Jobs        : {len(duplicate_jobs)}")

print("\n--- TOP LOCATIONS ---")
for loc, count in sorted(location_breakdown.items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f"  • {loc}: {count} jobs")

print("\n--- SAMPLE VALID JOBS PREVIEW (5 Samples) ---")
for i, sample in enumerate(valid_jobs[:5]):
    print(f"\n[Sample {i+1}]")
    print(f"  • Title       : {sample['title']}")
    print(f"  • Location    : {sample['location']}")
    print(f"  • Experience  : {sample['experience']}")
    print(f"  • Skills      : {sample['skills']}")
    print(f"  • Apply URL   : {sample['apply_url']}")
    print(f"  • JD Snippet  : {sample['desc_preview']}...")
