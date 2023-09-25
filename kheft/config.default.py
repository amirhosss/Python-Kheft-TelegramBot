from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    environment: str = "test"  # 'test' or 'production'

    webhook_url: str
    webhook_port: int

    backend_api_key: str
    backend_url: str

    telegrambot_token: str
    telegrambot_secret_roken: str
    telegrambot_proxy: str
    telegrambot_public_channel: str
    telegrambot_private_group: int

    book_price_limit: list

    class Config:
        case_sensitive = False


configs = Configs()
