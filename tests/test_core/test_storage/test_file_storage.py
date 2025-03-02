import os
import sys
import pytest
import shutil
from random import Random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.data_models.interview_data import InterviewData
from core.storage.file import FileStorage
from core.llm import ChatMessage


class TestFileStorage:
    @classmethod
    def setup_class(cls):
        # Create test directory
        os.makedirs("/tmp/test_data", exist_ok=True)
        
        # Initialize test objects
        cls.storage = FileStorage("/tmp/test_data")

    @classmethod
    def teardown_class(cls):
        # Clean up test directory
        if os.path.exists("/tmp/test_data"):
            shutil.rmtree("/tmp/test_data")
            
    def test_file_storage_instantiation(self):
        """Test file storage initialization"""
        assert self.storage.base_path == "/tmp/test_data"
    
    def test_file_storage_crud(self):
        """Test file storage check if interview data exists"""
        id = Random().randint(1, 1000)
        assert not self.storage.exists(id)
        
        data = InterviewData(
            id=id,
            progress=-1,
            history=[],
            messages=[],
            questions=["question1", "question2", "question3"]
        )
        
        self.storage.save(data)
        assert self.storage.exists(id)
        
        data = self.storage.load(id)
        assert data.id == id
        assert data.progress == -1
        assert data.history == []
        assert data.messages == []
        assert len(data.questions) == 3
    
        data.progress = 1
        data.messages.append(ChatMessage(role = "user", content = "Sure, I'd be happy to."))
        self.storage.save(data)
        loaded_data = self.storage.load(id)
        assert loaded_data.progress == 1
        assert loaded_data.messages[0] == ChatMessage(role = "user", content = "Sure, I'd be happy to.")
        
        
        