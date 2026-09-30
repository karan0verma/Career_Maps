def parse_ashby_graphql(data: dict, company_id: str, board_token: str) -> list:
    """Parses Ashby GraphQL response into raw dictionaries."""
    job_board = data.get("data", {}).get("jobBoard", {})
    if not job_board:
        return []

    teams_data = job_board.get("teams", [])
    team_map = {team["id"]: team["name"] for team in teams_data}

    postings = job_board.get("jobPostings", [])
    parsed_jobs = []

    for job in postings:
        job_id = job.get("id")
        title = job.get("title", "")
        location_name = job.get("locationName", "")
        
        team_id = job.get("teamId")
        department = team_map.get(team_id) if team_id else None
        
        apply_url = f"https://jobs.ashbyhq.com/{board_token}/{job_id}"
        
        # Heuristics for workplace and location
        workplace_type = None
        if location_name and "remote" in location_name.lower():
            workplace_type = "Remote"

        parsed_jobs.append({
            "externalJobId": job_id,
            "title": title,
            "location": location_name,
            "department": department,
            "team": department, # Ashby teams are essentially departments
            "workplaceType": workplace_type,
            "employmentType": job.get("employmentType"),
            "applyUrl": apply_url,
            "sourceATS": "ASHBY"
        })

    return parsed_jobs
