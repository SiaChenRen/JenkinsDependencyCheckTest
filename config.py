import os

class Config(object):
    # Web Server configs
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # KEYS
    SECRET_KEY = "dev" # Change to store in environment variable in the future
    WTF_CSRF_SECRET_KEY = "Test"

    # Database configs
    # MySQL database configs
    MYSQL_HOST = 'miahyap.ddns.net'
    MYSQL_USER = 'ssd_server'
    MYSQL_PASSWORD = 'Temp!Password123'
    MYSQL_DB = 'securetrade'
    # NoSQL database configs
    NOSQL_USER = 'securetrade'
    NOSQL_PASSWORD = 'Temp!Password123'
    NOSQL_INDEX_LOGS = 'securetrade-logs'
    NOSQL_INDEX_POSTS = 'securetrade-posts'
    NOSQL_INDEX_MESSAGING = 'securetrade-messaging'
    NOSQL_HOSTS = [{'host': 'miahdev.tech'}]

    # Other configs
    TOKEN_DURATION = 1800 # 30 min expiration

    # Tesseract server URL
    TESSERACT_URL = "https://tesseract.miahdev.tech"
    TESSERACT_API_KEY = 12341234
    
    # Mail configs
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'noreply.securetrade@gmail.com'
    MAIL_PASSWORD = 'qwerty1501'
    VERIFICATION_URL = 'securetrade.sitict.net/auth/verify'

    # File configs
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
