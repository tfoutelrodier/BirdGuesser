import logging
import os

class Config:
    # Default settings shared between all configurations

    CONFIG_NAME = 'default'

    # Data is stored in file server side because file could take a few Mb with sounds
    SESSION_TYPE = 'cachelib'
    SESSION_SERIALIZATION_FORMAT = 'json'
    SESSION_FILE_THRESHOLD = 500  # number of key:pair element that cache can hold before deleting elements
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'tmp', 'flask_sessions')
    SESSION_PERMANENT = False
    SESSION_TIMEOUT_SECONDS = 3600  # set session to expire after X second to free some space
    
    
    # for deployement specific configurations
    # for example, vercel needs different session storing path than local hosting
    HOSTING = os.getenv('HOSTING')

    TESTING = False
    DEBUG = False  # logging level

    SECRET_KEY = os.getenv('SECRET_KEY')

    # number of api call per second for xenocanto database
    API_TIME_WINDOW = 1  

    # logging
    LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    LOG_LEVEL = logging.INFO  # logging package default log levels


# for testing
class TestConfig(Config):
    CONFIG_NAME = 'testing'
    TESTING = True
    SECRET_KEY = os.getenv('TEST_SECRET_KEY')
    DEBUG = True
    LOGS_LEVEL = logging.DEBUG


# Standard config when coding
class DevConfig(Config):
    CONFIG_NAME = 'development'
    LOGS_LEVEL = logging.DEBUG


# Extra config to debug using dev environement settings
class DebugConfig(DevConfig):
    CONFIG_NAME = 'debug'
    DEBUG = True


# For vercel hosting
class VercelConfig(Config):
    CONFIG_NAME = 'vercel'
    SESSION_FILE_DIR = '/tmp'
    LOGS_DIR = '/tmp'


# How to access each config
config_dict = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": VercelConfig,
    "debug":DebugConfig
}