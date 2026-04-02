import os


class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL",
        "postgresql://landline:landline@localhost:5432/landline",
    )
    pool_min_size: int = int(os.environ.get("POOL_MIN_SIZE", "2"))
    pool_max_size: int = int(os.environ.get("POOL_MAX_SIZE", "10"))


settings = Settings()
