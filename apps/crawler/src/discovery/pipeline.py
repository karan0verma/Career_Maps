from abc import ABC, abstractmethod
from typing import Optional
from .models import Target

class PipelineStage(ABC):
    """
    Abstract base class for all stages in the Discovery Pipeline.
    Each stage receives a Target, modifies it, and returns it.
    """
    
    @abstractmethod
    def process(self, target: Target) -> Target:
        """
        Process the given target and return the modified target.
        """
        pass
