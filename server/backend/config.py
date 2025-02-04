# File: app/config.py
import os
import redis


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/clustroai'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@database-1.cojaa9n9bkqt.us-east-1.rds.amazonaws.com/clustroai'
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'session:'
    SESSION_REDIS = redis.StrictRedis(host=SQLALCHEMY_DATABASE_URI, port=6379, db=0)


class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@database-1.cojaa9n9bkqt.us-east-1.rds.amazonaws.com/clustroai'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST", "database-1.cojaa9n9bkqt.us-east-1.rds.amazonaws.com")}/clustroai'
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'session:'
    SESSION_REDIS = redis.StrictRedis(host=SQLALCHEMY_DATABASE_URI, port=6379, db=0)
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
