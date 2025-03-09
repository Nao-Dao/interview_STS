import os
import json
from .interview_base import InterviewStorage
from ..data_models.interview_data import InterviewData
from typing import Optional
from pathlib import Path
from ..utils.snowflake import generate_snowflake_id



class FileStorage(InterviewStorage):
    def __init__(self, base_path: str = "data") -> None:
        self.base_path = base_path
        
    def save(self, data: InterviewData) -> bool:
        try:
            file_content = data.model_dump_json(indent=2)
            json_path = os.path.join(self.base_path, str(data.id), "interview.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
            
    def load(self, interview_id: int) -> Optional[InterviewData]:
        try:
            json_path = os.path.join(self.base_path, str(interview_id), "interview.json")
            if not os.path.exists(json_path):
                return None
                
            with open(json_path, "r", encoding="utf-8") as f:
                return InterviewData.model_validate_json(f.read())
        except Exception as e:
            print(f"Error loading from file: {e}")
            return None
            
    def exists(self, interview_id: int) -> bool:
        json_path = os.path.join(self.base_path, str(interview_id), "interview.json")
        return os.path.exists(json_path)
    
    def save_audio(self, interview_id, data, format: str = None) -> str:
        audio_id = generate_snowflake_id()
        interview_audio_path = os.path.join(self.base_path,str(interview_id),"audios")
        if not os.path.exists(interview_audio_path):
            os.makedirs(interview_audio_path, exist_ok=True)
        audio_path = self._get_audio_file_path(interview_audio_path, audio_id, format)
        with open(audio_path, "wb") as f:
            f.write(data)
        return audio_path

    def _get_audio_file_path(self,interview_id_path, audio_id: int, format: str = None) -> str:
        matches = list(Path(interview_id_path).glob(f"{audio_id}*"))
        if len(matches)>0:
            base_path = matches[0]
        else:
            base_path = os.path.join(interview_id_path, str(audio_id))
        return f"{base_path}.{format}" if format else base_path 