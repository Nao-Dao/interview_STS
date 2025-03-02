import os

from enum import Enum
from .interview_base import InterviewStorage
from .mongo import MongoStorage
from .file import FileStorage

class StorageType(str, Enum):
    REMOTE = "remote"
    LOCAL = "local"

def create_storage(storage_type: str = None) -> InterviewStorage:
    """Create storage instance based on type"""
    if storage_type is None:
        storage_type = os.getenv("STORAGE_TYPE", "local")
    
    file_path = os.getenv("FILE_DATA_STORAGE_PATH", "data")

    match storage_type.lower():
        case StorageType.REMOTE:
            return MongoStorage()
        case StorageType.LOCAL:
            return FileStorage(file_path)
        case _:
            return FileStorage(file_path)