import os
import requests
from typing import Dict, Any, List

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:4000/api/v1")
        
    def get_queue(self, limit: int = 10) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/crawler/queue"
        try:
            response = requests.get(url, params={"limit": limit}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                return data.get("data", [])
            else:
                print(f"Error fetching queue: {data}")
                return []
        except Exception as e:
            print(f"Failed to fetch queue from API: {e}")
            return []

    def submit_result(self, result_payload: Dict[str, Any]) -> bool:
        url = f"{self.base_url}/crawler/result"
        try:
            response = requests.post(url, json=result_payload, timeout=30)
            response.raise_for_status()
            return response.json().get("success", False)
        except Exception as e:
            print(f"Failed to submit result to API: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(e.response.text)
            return False

    def send_heartbeat(self, status: str, uptime: float, error: str = None) -> bool:
        url = f"{self.base_url}/crawler/heartbeat"
        payload = {
            "status": status,
            "uptime": uptime
        }
        if error:
            payload["lastError"] = error
            
        try:
            response = requests.post(url, json=payload, timeout=5)
            return response.json().get("success", False)
        except Exception as e:
            print(f"Failed to send heartbeat: {e}")
            return False
