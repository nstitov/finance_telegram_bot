from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    bot_token: str
    bot_fsm_storage: str
    postgres_dsn: str
    redis_dsn: str

    @field_validator("bot_fsm_storage")
    @classmethod
    def validate_bot_fsm_storage(cls, v):
        if v not in ("memory", "redis"):
            raise ValueError(
                'Inorrect "bot_fsm_storage" value.' "Must be one of: memory, redis"
            )
        return v

    @field_validator("redis_dsn")
    @classmethod
    def validate_redis_dsn(cls, v, values):
        if values.data["bot_fsm_storage"] == "redis" and not v:
            raise ValueError("Redis DSN string is missing!")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


config = Config()
