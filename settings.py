from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str
    username: str
    password: str
    imai: int


settings = Settings()
