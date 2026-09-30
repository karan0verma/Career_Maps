import re
import json
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

class HtmlParserService:
    """A generic, ATS-agnostic utility for parsing HTML DOM structures."""
    
    @staticmethod
    def extract_script_content(html: str, regex_pattern: str) -> Optional[str]:
        """Finds a <script> tag whose text matches a regex and returns the match group or full script text."""
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                match = re.search(regex_pattern, script.string, re.DOTALL)
                if match:
                    # Return the first capturing group if exists, else the entire match
                    return match.group(1) if match.groups() else match.group(0)
        return None

    @staticmethod
    def extract_json_from_script(html: str, regex_pattern: str) -> Optional[Dict[str, Any]]:
        """Extracts text matching a regex from a script and parses it as JSON."""
        content = HtmlParserService.extract_script_content(html, regex_pattern)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    def extract_hidden_inputs(html: str) -> Dict[str, str]:
        """Extracts all <input type="hidden"> elements into a dictionary of name: value."""
        soup = BeautifulSoup(html, 'html.parser')
        hidden_inputs = soup.find_all('input', type='hidden')
        
        result = {}
        for inp in hidden_inputs:
            name = inp.get('name') or inp.get('id')
            if name:
                result[name] = inp.get('value', '')
        return result

    @staticmethod
    def extract_attribute(html: str, css_selector: str, attribute: str) -> Optional[str]:
        """Finds an element by CSS selector and returns the specified attribute."""
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.select_one(css_selector)
        if element:
            return element.get(attribute)
        return None

    @staticmethod
    def regex_search(html: str, pattern: str) -> Optional[str]:
        """Performs a raw regex search against the full HTML string."""
        match = re.search(pattern, html, re.DOTALL)
        if match:
            return match.group(1) if match.groups() else match.group(0)
        return None
