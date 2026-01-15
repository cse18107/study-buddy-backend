from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    CHAT_MODEL: str = "gpt-3.5-turbo"
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_HOST: str
    PINECONE_INDEX_NAME: str = "study-buddy"
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # JWT Settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 10  # 10 days

    class Config:
        env_file = ".env"

settings = Settings()