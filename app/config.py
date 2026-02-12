from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Email
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_username: str
    email_password: str
    email_from: str
    
    # App
    app_name: str = "Event Ticketing System"
    base_url: str = "http://localhost:8000"
    debug: bool = True
    secret_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()