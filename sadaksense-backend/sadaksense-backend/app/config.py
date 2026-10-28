from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://sadak:sadak@localhost:5432/sadaksense"
    redis_url: str = "redis://localhost:6379/0"
    routes_api_key: str = ""
    vlm_base_url: str = "http://localhost:8001/v1"
    vlm_model: str = "Qwen/Qwen3-VL-8B-Instruct"
    detector_weights: str = "weights/sadakvision_yolo26.pt"
    rqi_model_path: str = "weights/rqi_lgbm.txt"
    device: str = "cuda:0"
    conf_threshold: float = 0.35
    slice_size: int = 640


settings = Settings()
