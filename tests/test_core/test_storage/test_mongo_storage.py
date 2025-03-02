import pytest
import mongomock
from core.storage.mongo import MongoStorage
from core.data_models.interview_data import InterviewData
from core.llm import ChatMessage

class TestMongoStorage:
    @pytest.fixture(autouse=True)
    def setup_mock_mongo(self, monkeypatch):
        """Setup mock MongoDB client"""
        self.mock_client = mongomock.MongoClient()
        self.storage = MongoStorage()
        # Replace real MongoDB client with mock
        monkeypatch.setattr(self.storage, 'client', self.mock_client)
        monkeypatch.setattr(self.storage, 'db', self.mock_client.interview_sts)
        
    def test_save_and_load_interview(self):
        """Test saving and loading interview data"""
        # Create test data
        test_data = InterviewData(
            id=12345,
            progress=1,
            questions=["Test question"],
            history=[],
            messages=[
                ChatMessage(role="user", content="Test message")
            ]
        )
        
        # Test save
        assert self.storage.save(test_data)
        
        # Test load
        loaded_data = self.storage.load(12345)
        assert loaded_data is not None
        assert loaded_data.id == test_data.id
        assert loaded_data.progress == test_data.progress
        assert loaded_data.messages[0].content == "Test message"
        
    def test_exists_check(self):
        """Test checking if interview exists"""
        # Create and save test data
        test_data = InterviewData(
            id=12345,
            progress=0,
            questions=[],
            history=[],
            messages=[]
        )
        self.storage.save(test_data)
        
        # Test exists
        assert self.storage.exists(12345)
        assert not self.storage.exists(99999)