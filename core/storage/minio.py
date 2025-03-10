from minio import Minio
from io import BytesIO
from .interview_base import InterviewStorage
from ..data_models.interview_data import InterviewData
from typing import Optional
import os
import json
from ..utils.snowflake import generate_snowflake_id


class MinioStorage(InterviewStorage):
    """MinIO implementation of interview storage"""

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket_name: str = None,
        secure: bool = False,
    ):
        """Initialize MinIO client"""
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = bucket_name or os.getenv("MINIO_BUCKET", "interviews")

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=secure,
        )

        # Create bucket if not exists
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def _get_object_path(self, user_id: str) -> str:
        """Generate object path for interview data"""
        return f"{user_id}/interview.json"

    def _get_audio_object_path(
        self, user_id: str, audio_id: int, format: str
    ) -> str:
        base_path = f"{user_id}/audios/{audio_id}"
        return f"{base_path}.{format}" if format else base_path

    def save(self, data: InterviewData) -> bool:
        """Save interview data to MinIO"""
        try:
            json_data = data.model_dump_json(indent=2)
            data_bytes = json_data.encode("utf-8")
            data_length = len(data_bytes)

            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=self._get_object_path(data.user_id),
                data=BytesIO(data_bytes),
                length=len(data_bytes),
                content_type="application/json",
            )
            return bool(result and result.etag)
        except Exception as e:
            print(f"Error saving to MinIO: {e}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Object path: {self._get_object_path(data.user_id)}")
            return False

    def load(self, id: int) -> Optional[InterviewData]:
        """Load interview data from MinIO"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name, object_name=self._get_object_path(id)
            )
            json_data = response.read().decode("utf-8")
            return InterviewData.model_validate_json(json_data)
        except Exception as e:
            print(f"Error loading from MinIO: {e}")
            return None

    def exists(self, id: int) -> bool:
        """Check if interview exists in MinIO"""
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name, object_name=self._get_object_path(id)
            )
            return True
        except:
            return False

    def save_audio(self, user_id, data, format: str = None) -> str:
        try:
            audio_id = generate_snowflake_id()
            object_path = self._get_audio_object_path(user_id, audio_id, format)

            content_types = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "opus": "audio/opus",
                "ogg": "audio/ogg",
            }
            content_type = content_types.get(format, "application/octet-stream")

            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            if result and result.etag:
                return object_path
        except Exception as e:
            print(f"Error saving to MinIO: {e}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Object path: {object_path}")
            return False
        pass
