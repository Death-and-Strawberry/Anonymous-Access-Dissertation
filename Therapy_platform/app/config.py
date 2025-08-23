from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    secret_key: str = "dev-secret-key"
    debug: bool = False
    log_level: str = "INFO"
    app_port: int = 5000
    
    # Tor settings
    tor_control_password: Optional[str] = None
    tor_socks_port: int = 9050
    tor_control_port: int = 9051
    
    # Hidden service settings
    hidden_service_dir: str = "/var/lib/tor/myapp/"
    hidden_service_port: int = 80
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()