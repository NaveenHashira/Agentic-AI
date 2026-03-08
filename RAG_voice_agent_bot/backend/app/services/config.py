from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # MongoDb settings
    MONGO_URL : str
    DB_NAME : str = "live_db"

    # Tell Pydantic where to look for the file
    model_config = SettingsConfigDict(env_file=".env")

# Create the settings object
settings = Settings()