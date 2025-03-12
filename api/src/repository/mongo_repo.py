import motor.motor_asyncio as motor
from yarl import URL

from src.repository.base_repo import IDatabaseRepository
from common_utils.log_util import setup_file_logger


ASCENDING = 1
DESCENDING = -1

logger = setup_file_logger(
    name="mongo_logger", log_file="mongo_logger.log")

class MongodbRepository(IDatabaseRepository):
    _instance = None

    def __new__(cls, database_url: URL, database_name: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__client = motor.AsyncIOMotorClient(str(database_url))
            cls._instance.__db = cls._instance.__client[database_name]
            cls._instance.logger = logger
        return cls._instance

    async def find_one(self, collection_name: str, query: dict):
        try:
            result = await self.__db[collection_name].find_one(query, projection={"_id": False})
            return result
        except Exception as e:
            self.logger.error(f"Error searching the document:\n{e}")
            raise


    async def insert_one(self, collection_name: str, document: dict):
        try:
            result = await self.__db[collection_name].insert_one(document)
            return result
        except Exception as e:
            self.logger.error(f"Error adding the document:\n{e}")
            raise




