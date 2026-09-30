import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any

class XmlParserService:
    """A generic, ATS-agnostic utility for safe XML parsing and manipulation."""
    
    @staticmethod
    def parse_string(xml_str: str) -> Optional[ET.Element]:
        """Safely parses an XML string into an ElementTree root node."""
        try:
            return ET.fromstring(xml_str)
        except ET.ParseError:
            return None

    @staticmethod
    def find_all_elements(root: ET.Element, xpath_query: str) -> List[ET.Element]:
        """Wrapper around ElementTree's findall for fetching all matching nodes."""
        if root is None:
            return []
        return root.findall(xpath_query)

    @staticmethod
    def node_to_dict(element: ET.Element) -> Dict[str, Any]:
        """
        Recursively converts an XML Element and its children into a native Python dictionary.
        Attributes are stored under '@attribute_name'.
        Text content is stored under '#text' if the node has both attributes and text,
        or as a direct value if it's a simple text node.
        """
        if element is None:
            return {}
            
        result = {}
        
        # Add attributes
        if element.attrib:
            for k, v in element.attrib.items():
                result[f"@{k}"] = v
                
        # Add children
        children = list(element)
        if children:
            for child in children:
                child_dict = XmlParserService.node_to_dict(child)
                # If tag already exists, convert to list
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
        else:
            # No children, just text
            text = element.text.strip() if element.text else ""
            if result:
                # Has attributes
                if text:
                    result["#text"] = text
            else:
                # No attributes, just text
                return text
                
        return result
