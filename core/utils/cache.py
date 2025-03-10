import os
from glob import glob
from .snowflake import generate_snowflake_id

class Cache():
    SAVE_PATH = "data/TEMP"

    def __init__(self) -> None:
        if not os.path.exists(self.SAVE_PATH):
            os.mkdir(self.SAVE_PATH)

    def save(self, data, format: str = None) -> int:
        if not os.path.exists(self.SAVE_PATH):
            os.mkdir(self.SAVE_PATH)
        cache_id = generate_snowflake_id()
        path = self.get_path(cache_id) if format is None else "%s.%s" % (self.get_path(cache_id), format)
        if isinstance(data, str):
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
        elif isinstance(data, bytes):
            with open(path, "wb") as f:
               f.write(data)
        else:
            raise NotImplementedError()
        return cache_id

    def load(self, cid: int, t: str = "str"):
        path = self.get_path(cid)
        if not os.path.exists(path):
            return None
        if t == "str":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            with open(path, "rb") as f:
                return f.read()

    def get_path(self, cid: int):
        path = glob("%s/%s*" % (self.SAVE_PATH, cid))
        if len(path):
            return path[0]
        return os.path.join(self.SAVE_PATH, str(cid))

cache = Cache()


