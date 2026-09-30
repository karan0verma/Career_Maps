from typing import Any, Dict, List, Tuple

class ResponseScorer:
    """
    Scores JSON responses to determine if they contain job posting data.
    """
    
    JOB_SIGNALS = {
        'title': ['title', 'jobtitle', 'position', 'role', 'name', 'job_title'],
        'id': ['id', 'jobid', 'requisitionid', 'externalid', 'reqid', 'job_id'],
        'location': ['location', 'locations', 'city', 'country', 'state'],
        'description': ['description', 'jobdescription', 'summary'],
        'url': ['applyurl', 'applicationurl', 'url', 'joburl', 'apply', 'link']
    }
    
    ANTI_SIGNALS = ['news', 'blog', 'product', 'category', 'users', 'analytics', 'tracking', 'advertisement', 'nav']
    
    @classmethod
    def score_response(cls, data: Any) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Recursively scores the response data.
        Returns a tuple: (score, extracted_job_array)
        """
        best_score = 0
        best_list = []
        
        if isinstance(data, list):
            score = cls._score_list(data)
            if score > best_score:
                best_score = score
                best_list = data
                
            # Keep digging just in case the list contains nested objects that are even better
            for item in data:
                if isinstance(item, dict):
                    child_score, child_list = cls.score_response(item)
                    if child_score > best_score:
                        best_score = child_score
                        best_list = child_list
                        
        elif isinstance(data, dict):
            # Try to score any child lists
            for key, val in data.items():
                if isinstance(val, list):
                    score = cls._score_list(val)
                    if score > best_score:
                        best_score = score
                        best_list = val
                        
                    # Also dig into the child list items
                    for item in val:
                        if isinstance(item, dict):
                            child_score, child_list = cls.score_response(item)
                            if child_score > best_score:
                                best_score = child_score
                                best_list = child_list
                elif isinstance(val, dict):
                    child_score, child_list = cls.score_response(val)
                    if child_score > best_score:
                        best_score = child_score
                        best_list = child_list
                        
        return best_score, best_list

    @classmethod
    def _score_list(cls, data_list: List[Any]) -> int:
        if not data_list:
            return 0
            
        total_score = 0
        valid_items = 0
        
        # Sample up to 5 items to determine the score
        for item in data_list[:5]:
            if isinstance(item, dict):
                item_score = cls._score_item(item)
                if item_score > 0:
                    total_score += item_score
                    valid_items += 1
                    
        # If multiple items have strong job signals, increase score multiplier
        if valid_items > 0:
            return total_score + (valid_items * 2)
        return 0
        
    @classmethod
    def _score_item(cls, item: Dict[str, Any]) -> int:
        score = 0
        keys = set(str(k).lower() for k in item.keys())
        
        # Flatten string values for deep keyword check
        values_str = " ".join([str(v).lower() for v in item.values() if isinstance(v, str)])
        
        # Check Title
        if any(sig in keys for sig in cls.JOB_SIGNALS['title']):
            score += 3
            
        # Check ID
        if any(sig in keys for sig in cls.JOB_SIGNALS['id']):
            score += 2
            
        # Check Location
        if any(sig in keys for sig in cls.JOB_SIGNALS['location']):
            score += 2
            
        # Check Description
        if any(sig in keys for sig in cls.JOB_SIGNALS['description']):
            score += 1
            
        # Check URL
        if any(sig in keys for sig in cls.JOB_SIGNALS['url']):
            score += 2
            
        # Anti-signals
        if any(any(anti in k for anti in cls.ANTI_SIGNALS) for k in keys):
            score -= 5
            
        if any(anti in values_str for anti in cls.ANTI_SIGNALS):
            score -= 2
            
        return score
