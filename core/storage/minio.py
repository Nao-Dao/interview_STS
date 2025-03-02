
from minio import Minio
from io import BytesIO
from .interview_base import InterviewStorage
from ..data_models.interview_data import InterviewData
from typing import Optional
import os
import json

class MinioStorage(InterviewStorage):
    """MinIO implementation of interview storage"""
    
    def __init__(self, 
                 endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 bucket_name: str = None,
                 secure: bool = False):
        """Initialize MinIO client"""
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = bucket_name or os.getenv("MINIO_BUCKET", "interviews")
        
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=secure
        )
        
        # Create bucket if not exists
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
    
    def _get_object_path(self, id: int) -> str:
        """Generate object path for interview data"""
        return f"{id}/data.json"
    
    def save(self, data: InterviewData) -> bool:
        """Save interview data to MinIO"""
        try:
            json_data = data.model_dump_json(indent=2)
            data_bytes = json_data.encode('utf-8')
            data_length = len(data_bytes)
            
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=self._get_object_path(data.id),
                data=BytesIO(data_bytes),
                length=len(data_bytes),
                content_type='application/json'
            )
            return bool(result and result.etag)
        except Exception as e:
            print(f"Error saving to MinIO: {e}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Object path: {self._get_object_path(data.id)}")
            return False
    
    def load(self, id: int) -> Optional[InterviewData]:
        """Load interview data from MinIO"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=self._get_object_path(id)
            )
            json_data = response.read().decode('utf-8')
            return InterviewData.model_validate_json(json_data)
        except Exception as e:
            print(f"Error loading from MinIO: {e}")
            return None
    
    def exists(self, id: int) -> bool:
        """Check if interview exists in MinIO"""
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=self._get_object_path(id)
            )
            return True
        except:
            return False