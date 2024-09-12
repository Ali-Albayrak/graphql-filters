from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import event

from core.logger import log
from core.constants import AppConstants as AC


Base = declarative_base()

db_url = f'{AC.DB_DRIVER}://{AC.DB_USERNAME}:{AC.DB_PASSWORD}@{AC.DB_HOST}:{AC.DB_PORT}/{AC.DB_NAME}?{AC.DB_QUERY_PARAMS}'

engine_args = {
    "pool_size": AC.DB_POOL_SIZE,
    "max_overflow": AC.DB_MAX_OVERFLOW,
    "pool_timeout": AC.DB_POOL_TIMEOUT,
    "pool_recycle": AC.DB_POOL_RECYCLE,
}
engine_async = create_async_engine(db_url, echo=True, **engine_args)
db_session: AsyncSession = sessionmaker(bind=engine_async, expire_on_commit=False, class_=AsyncSession)
