from abc import ABC, abstractmethod
from ..data_models.audio_message import AudioMessage
from typing import Optional, Protocol

class AudioStorage(ABC):
    """Abstract base class for interview data storage"""
    
    @abstractmethod
    def save(self, data, format: str = None) -> int:
        """Save audio data
        
        Args:
            data: audio data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def load(self, cid: int, t: str = "str"):
        """Load audio data
        
        Args:
            id: Interview ID to load
            
        Returns:
            Optional[InterviewData]: Interview data if found, None otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_path(self, cid: int) -> str:
        """Check if interview exists
        
        Args:
            id: Interview ID to check
            
        Returns:
            bool: True if interview exists, False otherwise
        """
        raise NotImplementedError