import os
import sys
import pytest
import shutil
from random import Random

from core.llm import ChatMessage

from core.interview import InterviewManager
from core.storage.file import FileStorage

from core.storage.minio import MinioStorage
from unittest.mock import MagicMock
from io import BytesIO
from core.data_models.interview_data import InterviewData

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestInterview:
    @pytest.fixture(autouse=True)
    def setup_env_vars(self, monkeypatch):
        os.makedirs("/tmp/test_data", exist_ok=True)
        
        # Cleanup after tests
        yield
        if os.path.exists("/tmp/test_data"):
            shutil.rmtree("/tmp/test_data")

    def test_interview_manager_can_load_and_update_messages_from_local_file(self, monkeypatch):
        """Test interview manager initialization"""
        monkeypatch.setenv("STORAGE_TYPE", "local")
        monkeypatch.setenv("FILE_DATA_STORAGE_PATH", "/tmp/test_data")
        interview_manager = InterviewManager()
        assert interview_manager.storage.base_path == "/tmp/test_data"
        assert isinstance(interview_manager.storage, FileStorage)
        data = interview_manager.load_data(interview_manager.id)
        data.progress = 1
        data.messages.append(ChatMessage(role = "user", content = "Sure, I'd be happy to."))
        interview_manager.save_data(data)
        
        loaded_data = interview_manager.load_data(interview_manager.id)
        assert loaded_data.progress == 1
        assert loaded_data.messages[0] == ChatMessage(role = "user", content = "Sure, I'd be happy to.")
   
    def test_interview_manager_can_load_and_update_messages_from_local_file(self, monkeypatch):
        monkeypatch.setenv("STORAGE_TYPE", "notexist")
        with pytest.raises(ValueError, match=r"Invalid storage type.*"):
            interview_manager = InterviewManager()

    def test_interview_manager_can_load_and_update_messages_from_minio(self, monkeypatch):
        monkeypatch.setenv("STORAGE_TYPE", "remote")
        mock_client = MagicMock()
        mock_client.put_object.return_value = None
      
        interview_manager = InterviewManager()
        assert isinstance(interview_manager.storage, MinioStorage)
        interview_manager.storage.client = mock_client
        
        initial_data = InterviewData(
            id=interview_manager.id,
            progress=-1,
            history=[],
            messages=[],
            questions=["Test question"]
        )
        
        mock_client.get_object.return_value = BytesIO(
            initial_data.model_dump_json().encode('utf-8')
        )
        
        data = interview_manager.load_data(interview_manager.id)
        data.progress = 1
        data.messages.append(ChatMessage(role = "user", content = "Sure, I'd be happy to."))
        interview_manager.save_data(data)
        
        mock_client.get_object.return_value = BytesIO(
            data.model_dump_json().encode('utf-8')
        )
    
        loaded_data = interview_manager.load_data(interview_manager.id)
        assert loaded_data.progress == 1
        assert loaded_data.messages[0] == ChatMessage(role = "user", content = "Sure, I'd be happy to.")
        
