import pytest
from unittest.mock import MagicMock
from core.storage.minio import MinioStorage
from core.data_models.interview_data import InterviewData
from core.llm import ChatMessage
from io import BytesIO
from core.storage.minio import MinioStorage
import uuid



class TestMinioStorage:
    @pytest.fixture(autouse=True)
    def setup_minio(self, monkeypatch):
        """Setup test environment"""
        self.mock_client = MagicMock()
        self.storage = MinioStorage()
        self.user_id = str(uuid.uuid4())
        monkeypatch.setattr(self.storage, "client", self.mock_client)

    def test_save_interview(self):
        """Test saving interview data"""
        test_data = InterviewData(
            user_id=self.user_id ,
            progress=0,
            questions=["Test question"],
            history=[],
            messages=[ChatMessage(role="user", content="Test message")],
        )

        self.mock_client.put_object.return_value = MagicMock(etag="test_etag")
        assert self.storage.save(test_data)
        self.mock_client.put_object.assert_called_once()

    def test_load_interview(self):
        """Test loading interview data"""
        test_data = InterviewData(
            user_id=self.user_id, progress=0, questions=[], history=[], messages=[]
        )

        self.mock_client.get_object.return_value = BytesIO(
            test_data.model_dump_json().encode("utf-8")
        )

        loaded_data = self.storage.load(12345)
        assert loaded_data is not None
        assert loaded_data.user_id == test_data.user_id
