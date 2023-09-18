from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    environment: str = "test" # 'test' or 'production'

    api_key: str

    telegrambot_token: str 
    telegrambot_proxy: str
    telegrambot_public_channel: str

    advertise_price: int

    book_price_limit: list = []

    class Config:
        case_sensitive = False


configs = Configs()