import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Blockchain configuration
    BLOCKCHAIN_MINING_INTERVAL = 10  # seconds
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///instance/voting_system.db'
    
    # Development-specific settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
    # Enable detailed error pages
    TESTING = False
    
    # Development logging
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///instance/test_voting_system.db'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production database (PostgreSQL recommended)
    # Normalize Render's postgres URL to SQLAlchemy's expected scheme
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url:
        if _raw_db_url.startswith('postgres://'):
            _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = _raw_db_url
        print(f"[ProductionConfig] Using DATABASE_URL from environment: {_raw_db_url[:50]}...")
    else:
        # In production, DATABASE_URL should always be set
        # Log warning but allow fallback for local testing
        import warnings
        warnings.warn('WARNING: DATABASE_URL not set in production! Falling back to SQLite.')
        print("[ProductionConfig] WARNING: DATABASE_URL not set! Using SQLite fallback.")
        SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'sqlite:///instance/voting_system.db'
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production logging
    LOG_LEVEL = 'INFO'
    
    # Disable detailed error pages
    PROPAGATE_EXCEPTIONS = False
    
    # Production-specific settings
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

class StagingConfig(ProductionConfig):
    """Staging configuration (similar to production but with some debugging)"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    
    # Staging-specific settings
    SESSION_COOKIE_SECURE = False  # Allow HTTP for staging

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment variable"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, DevelopmentConfig)
