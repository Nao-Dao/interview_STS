import os
import json
from .interview_base import InterviewStorage
from ..data_models.interview_data import InterviewData
from typing import Optional


class FileStorage(InterviewStorage):
    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        
    def save(self, data: InterviewData) -> bool:
        try:
            file_content = data.model_dump_json(indent=2)
            json_path = os.path.join(self.base_path, "interview", f"{data.id}.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
            
    def load(self, id: int) -> Optional[InterviewData]:
        try:
            json_path = os.path.join(self.base_path, "interview", f"{id}.json")
            if not os.path.exists(json_path):
                return None
                
            with open(json_path, "r", encoding="utf-8") as f:
                return InterviewData.model_validate_json(f.read())
        except Exception as e:
            print(f"Error loading from file: {e}")
            return None
            
    def exists(self, id: int) -> bool:
        json_path = os.path.join(self.base_path, "interview", f"{id}.json")
        return os.path.exists(json_path)
    