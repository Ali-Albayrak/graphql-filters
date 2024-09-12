import os
import json
from typing import List


class AppConstants:
    """
    AppConstants class
    """
    WELL_KNOWN_URLS: dict = json.loads(os.getenv("WELL_KNOWN_URLS", '{}'))
    ZEAUTH_BASE_URL: str = WELL_KNOWN_URLS.get('zekoder-zeauth-service-base-url')
    ZENOTIFY_BASE_URL: str = WELL_KNOWN_URLS.get('zekoder-zenotify-local-address')
    INTERNAL_IP_RANGES: str = os.getenv("INTERNAL_IP_RANGES") 

    # database credentials
    DB_USERNAME: str = os.environ.get('DB_USERNAME', 'demo')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD', 'demo29517')
    DB_NAME: str = os.environ.get('DB_NAME', 'zekoder')
    DB_HOST: str = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT: str = os.environ.get('DB_PORT', '26257')

    # engine client config
    DB_POOL_SIZE: str = os.environ.get('DB_POOL_SIZE', 10)
    DB_MAX_OVERFLOW: str = os.environ.get('DB_POOL_SIZE', 5)
    DB_POOL_TIMEOUT: str = os.environ.get('DB_POOL_SIZE', 30) #30 seconds
    DB_POOL_RECYCLE: str = os.environ.get('DB_POOL_SIZE', 3600) #1 hour
    DB_SYNC_DRIVER: str = os.environ.get('SYNC_DB_DRIVER', 'postgresql+psycopg2')
    SYNC_DB_QUERY_PARAMS: str = os.environ.get('SYNC_DB_QUERY_PARAMS', 'sslmode=disable')
    DB_DRIVER: str = os.environ.get('DB_DRIVER', 'postgresql+asyncpg')
    DB_QUERY_PARAMS: str = os.environ.get('DB_QUERY_PARAMS', 'ssl=disable')

    # Error template format
    ERROR_TEMPLATE = "Error inside {0}:  An exception of type {1} occurred. error: {2}"


def get_internal_ip_ranges() -> List[str]:
    """
    Return array of internal ip ranges
    """
    if AppConstants.INTERNAL_IP_RANGES is None:
        raise ValueError("INTERNAL_IP_RANGES environment variable is not set. Please set it before running the application.")
    return AppConstants.INTERNAL_IP_RANGES.split(',')

