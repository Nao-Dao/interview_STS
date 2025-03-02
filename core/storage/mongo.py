from pymongo import MongoClient
from .interview_base import InterviewStorage
from ..data_models.interview_data import InterviewData
from typing import Optional

import os

class MongoStorage(InterviewStorage):
    def __init__(self, uri: str = None):
        if uri is None:
            uri = os.getenv("MONGODB_URI", "mongodb://admin:password@localhost:27017/")
        self.client = MongoClient(uri)
        self.db = self.client.interview_sts
        
    def save(self, data: InterviewData) -> bool:
        try:
            collection = self.db.interviews
            doc = data.model_dump()
            result = collection.update_one(
                {"id": doc["id"]},
                {"$set": doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return False
            
    def load(self, id: int) -> Optional[InterviewData]:
        try:
            collection = self.db.interviews
            doc = collection.find_one({"id": id})
            if doc:
                return InterviewData.model_validate(doc)
            return None
        except Exception as e:
            print(f"Error loading from MongoDB: {e}")
            return None
            
    def exists(self, id: int) -> bool:
        try:
            collection = self.db.interviews
            return collection.count_documents({"id": id}) > 0
        except Exception as e:
            print(f"Error checking MongoDB: {e}")
            return False