from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm:str
    access_token_expire_minutes: int
    database_url: str

    model_config = {
        "env_file": ".env"
    }

settings = Settings()



