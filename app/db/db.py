import logging

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from conf.config import Config
from models.user import User
from models.story import Story

load_dotenv()

db_client: AsyncIOMotorClient = None


async def get_db() -> AsyncIOMotorClient:
    db_name = Config.app_settings.get('db_name')
    return db_client[db_name]


async def connect_and_init_db():
    global db_client
    try:
        db_client = AsyncIOMotorClient(
            Config.app_settings.get('mongodb_url'),
            username=Config.app_settings.get('db_username'),
            password=Config.app_settings.get('db_password'),
            maxPoolSize=Config.app_settings.get('max_db_conn_count'),
            minPoolSize=Config.app_settings.get('min_db_conn_count'),
            uuidRepresentation="standard",
        )
        await init_beanie(db_client.account, document_models=[User,Story]) 
        logging.info('Connected to mongo.')
    except Exception as e:
        logging.exception(f'Could not connect to mongo: {e}')
        raise


async def close_db_connect():
    global db_client
    if db_client is None:
        logging.warning('Connectosn is None, nothing to close.')
        return
    db_client.close()
    db_client = None
    logging.info('Mongo connection closed.')
