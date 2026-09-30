def parse_workable_json(jobs: list, company_id: str, board_token: str) -> list:
    """Parses Workable API response into raw dictionaries."""
    parsed_jobs = []

    for job in jobs:
        job_id = job.get("shortcode")
        if not job_id:
            job_id = job.get("id")
            
        title = job.get("title", "")
        
        location_obj = job.get("location", {})
        city = location_obj.get("city")
        region = location_obj.get("region")
        country = location_obj.get("country")
        
        loc_parts = [p for p in [city, region, country] if p]
        location_str = ", ".join(loc_parts) if loc_parts else "Unknown"
        
        is_remote = job.get("remote", False)
        
        # Workable explicitly returns 'workplace' (e.g. 'remote', 'hybrid', 'onsite')
        workplace_raw = job.get("workplace")
        workplace_type = None
        if workplace_raw:
            if workplace_raw.lower() == "remote": workplace_type = "Remote"
            elif workplace_raw.lower() == "hybrid": workplace_type = "Hybrid"
            elif workplace_raw.lower() == "onsite": workplace_type = "On-site"
        elif is_remote:
            workplace_type = "Remote"
            
        department = job.get("department")
        apply_url = f"https://apply.workable.com/{board_token}/j/{job_id}/"

        parsed_jobs.append({
            "externalJobId": job_id,
            "title": title,
            "location": location_str,
            "city": city,
            "state": region,
            "country": country,
            "department": department,
            "workplaceType": workplace_type,
            "employmentType": job.get("type"),
            "publishedAt": job.get("published"),
            "applyUrl": apply_url,
            "sourceATS": "WORKABLE"
        })

    return parsed_jobs
