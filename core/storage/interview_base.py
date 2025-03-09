from abc import ABC, abstractmethod
from ..data_models.interview_data import InterviewData
from typing import Optional, Protocol

class InterviewStorage(ABC):
    """Abstract base class for interview data storage"""
    
    @abstractmethod
    def save(self, data: InterviewData) -> bool:
        """Save interview data
        
        Args:
            data: Interview data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def load(self, interview_id: int) -> Optional[InterviewData]:
        """Load interview data
        
        Args:
            interview_id: Interview interview_id to load
            
        Returns:
            Optional[InterviewData]: Interview data if found, None otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def exists(self, interview_id: int) -> bool:
        """Check if interview exists
        
        Args:
            interview_id: Interview interview_id to check
            
        Returns:
            bool: True if interview exists, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def save_audio(self, interview_id, data, format: str = None) -> str:
        """Save audio data
        
        Args:
            data: audio data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        raise NotImplementedError 
