import importlib
import pkgutil
from typing import Dict, Type

class AtsRegistry:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, ats_type: str):
        """Decorator to register an ATS adapter by its AtsType."""
        def wrapper(crawler_class):
            cls._registry[ats_type.upper()] = crawler_class
            return crawler_class
        return wrapper

    @classmethod
    def get(cls, ats_type: str) -> Type:
        """Retrieve an ATS adapter by its AtsType (e.g., 'WORKDAY')."""
        return cls._registry.get((ats_type or "UNKNOWN").upper())

    @classmethod
    def load_adapters(cls, package_name: str = "src.ats.adapters"):
        """Dynamically import all modules in the given package so they register themselves."""
        try:
            package = importlib.import_module(package_name)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                if is_pkg:
                    importlib.import_module(f"{package_name}.{module_name}.crawler")
        except ModuleNotFoundError:
            pass
