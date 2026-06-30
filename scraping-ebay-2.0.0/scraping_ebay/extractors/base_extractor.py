from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """
    base class for all extractors
    """
    
    @abstractmethod
    def extract(self, response):
        """
        Extract a domain model
        """
        raise NotImplementedError