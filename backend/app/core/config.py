from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OPiN"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database URLs
    MONGODB_URL: str
    INFLUXDB_URL: str
    REDIS_URL: str
    
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CONSUMER_GROUP: str = "opin-consumer-group"
    
    # PI Network Settings
    PI_NETWORK_API_KEY: str
    PI_NETWORK_API_URL: str
    
    # ZKP Settings
    ZKP_PROVING_KEY_PATH: str = "./keys/proving.key"
    ZKP_VERIFICATION_KEY_PATH: str = "./keys/verification.key"
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# API Key validation
def validate_api_key(api_key: str, settings: Settings) -> bool:
    """
    Validate API key against stored keys
    In production, this would check against a secure key store
    """
    # Implement proper API key validation
    return True

# Database connection configurations
def get_mongodb_settings(settings: Settings) -> Dict[str, Any]:
    """Get MongoDB connection settings"""
    return {
        "host": settings.MONGODB_URL,
        "maxPoolSize": 100,
        "minPoolSize": 10,
        "maxIdleTimeMS": 5000,
        "retryWrites": True,
    }

def get_influxdb_settings(settings: Settings) -> Dict[str, Any]:
    """Get InfluxDB connection settings"""
    return {
        "url": settings.INFLUXDB_URL,
        "org": "opin",
        "timeout": 10000,
        "verify_ssl": True,
    }

def get_redis_settings(settings: Settings) -> Dict[str, Any]:
    """Get Redis connection settings"""
    return {
        "url": settings.REDIS_URL,
        "encoding": "utf-8",
        "decode_responses": True,
        "socket_timeout": 5,
    }

def get_kafka_settings(settings: Settings) -> Dict[str, Any]:
    """Get Kafka connection settings"""
    return {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
        "group_id": settings.KAFKA_CONSUMER_GROUP,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
        "max_poll_interval_ms": 300000,
    }

# Environment-specific configurations
class DevelopmentSettings(Settings):
    class Config:
        env_file = ".env.development"

class ProductionSettings(Settings):
    class Config:
        env_file = ".env.production"

class TestSettings(Settings):
    class Config:
        env_file = ".env.test"

# Factory function for settings
def get_environment_settings(environment: str = "development") -> Settings:
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "test": TestSettings,
    }
    settings_class = settings_map.get(environment, Settings)
    return settings_class()