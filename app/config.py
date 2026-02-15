from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Email
    email_host: Optional[str] = "smtp.gmail.com"
    email_port: Optional[int] = 587
    email_username: Optional[str] = None
    email_password: str  # This is the SendGrid API key
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