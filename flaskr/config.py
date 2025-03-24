import os

class Config:
    # Default settings shared between all configurations

    # Data is stored in file server side because file could take a few Mb with sounds
    SESSION_TYPE = 'filesystem'

    # storing flask session file with filesystem mode
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'tmp', 'flask_sessions')
    SESSION_PERMANENT = False

    # for deployement specific configurations
    # for example, vercel needs different session storing path than local hosting
    HOSTING = os.getenv('HOSTING')

    TESTING = False
    DEBUG = False  # logging level

    SECRET_KEY = os.getenv('SECRET_KEY')

    # number of api call per second for xenocanto database
    API_TIME_WINDOW = 1  


# for testing
class TestConfig(Config):
    TESTING = True


# Standard config when coding
class DevConfig(Config):
    DEBUG = True


# For vercel hosting
class VercelConfig(Config):
    SESSION_FILE_DIR = '/tmp'


# How to access each config
config_dict = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": VercelConfig,
}