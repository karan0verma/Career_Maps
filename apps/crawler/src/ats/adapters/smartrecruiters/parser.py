def parse_smartrecruiters_json(jobs: list, company_id: str) -> list:
    """Parses SmartRecruiters API response into raw dictionaries."""
    parsed_jobs = []

    for job in jobs:
        job_id = job.get("id")
        title = job.get("name", "")
        
        location_obj = job.get("location", {})
        city = location_obj.get("city")
        region = location_obj.get("region")
        country = location_obj.get("country")
        
        loc_parts = [p for p in [city, region, country] if p]
        location_str = ", ".join(loc_parts) if loc_parts else "Unknown"
        
        is_remote = location_obj.get("remote", False)
        workplace_type = "Remote" if is_remote else None
        
        department_obj = job.get("department", {})
        department = department_obj.get("label")
        
        # Base web URL instead of API url
        company_identifier = job.get('company', {}).get('identifier', '')
        apply_url = f"https://jobs.smartrecruiters.com/{company_identifier}/{job_id}"
        
        # If postingUrl is available (often is in detail views)
        if job.get("postingUrl"):
            apply_url = job.get("postingUrl")
        
        # Get description if present (e.g., from detailed fetch or jobAd)
        description = ""
        job_ad = job.get("jobAd", {})
        if job_ad and isinstance(job_ad.get("sections"), dict):
            sections = job_ad["sections"]
            desc_text = sections.get("jobDescription", {}).get("text", "")
            qual_text = sections.get("qualifications", {}).get("text", "")
            description = f"{desc_text}<br/>{qual_text}"
        
        parsed_jobs.append({
            "externalJobId": job_id,
            "title": title,
            "description": description,
            "location": location_str,
            "city": city,
            "state": region,
            "country": country,
            "department": department,
            "workplaceType": workplace_type,
            "employmentType": job.get("typeOfEmployment", {}).get("label"),
            "publishedAt": job.get("releasedDate"),
            "applyUrl": apply_url,
            "sourceATS": "SMARTRECRUITERS"
        })

    return parsed_jobs
