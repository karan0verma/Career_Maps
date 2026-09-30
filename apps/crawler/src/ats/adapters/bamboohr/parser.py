from typing import Dict, Any, List

class BambooHRParser:
    @staticmethod
    def parse_jobs(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Locates the jobs array inside the BambooHR embedded JSON or API payload
        and extracts it into a list of normalized raw dictionaries.
        """
        raw_jobs = []
        
        # Determine where the jobs are stored based on the payload structure
        jobs_list = []
        if 'result' in raw_data and isinstance(raw_data['result'], list):
            # API fallback payload
            jobs_list = raw_data['result']
        elif 'data' in raw_data and isinstance(raw_data['data'], list):
            jobs_list = raw_data['data']
        else:
            # Recursive search for a list containing job nodes (e.g. 'jobTitle' key)
            def find_jobs_array(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_jobs_array(v)
                        if res is not None:
                            return res
                elif isinstance(obj, list):
                    if len(obj) > 0 and isinstance(obj[0], dict) and 'jobTitle' in obj[0]:
                        return obj
                    for item in obj:
                        res = find_jobs_array(item)
                        if res is not None:
                            return res
                return None
                
            found = find_jobs_array(raw_data)
            if found:
                jobs_list = found
                
        for job in jobs_list:
            mapped = {
                "externalJobId": str(job.get("id")) if job.get("id") else None,
                "title": job.get("jobTitle") or job.get("title"),
                "description": job.get("description"),
                "location": job.get("location") or job.get("city"), # BambooHR can have nested locations
                "department": job.get("department"),
                "team": None,
                "workplaceType": job.get("workplaceType") or job.get("remote"),
                "publishedAt": job.get("postedDate") or job.get("published"),
                "applyUrl": None,
                "jobUrl": None
            }
            
            # Construct jobUrl if we have the id
            if mapped["externalJobId"]:
                # The token is not directly accessible here, so we will let BaseCrawler handle the domain
                # or build a relative path
                mapped["jobUrl"] = f"/careers/{mapped['externalJobId']}"
                
            # If location is a dict
            loc = job.get("location")
            if isinstance(loc, dict):
                city = loc.get("city", "")
                state = loc.get("state", "")
                country = loc.get("country", "")
                mapped["location"] = ", ".join(filter(None, [city, state, country]))
                
            raw_jobs.append(mapped)
            
        return raw_jobs
