import os
import sys
import pytest
import shutil
from random import Random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.interview import InterviewManager
from core.storage.file import FileStorage
from core.llm import ChatMessage

class TestInterview:
    @pytest.fixture(autouse=True)
    def setup_env_vars(self, monkeypatch):
        monkeypatch.setenv("STORAGE_TYPE", "file")
        monkeypatch.setenv("FILE_DATA_STORAGE_PATH", "/tmp/test_data")
        
        os.makedirs("/tmp/test_data", exist_ok=True)
        
        # Cleanup after tests
        yield
        if os.path.exists("/tmp/test_data"):
            shutil.rmtree("/tmp/test_data")

    def test_interview_manager_can_load_and_update_messages(self):
        """Test interview manager initialization"""
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
   