from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Storage
    azure_storage_blob_endpoint: str = ""

    # Cosmos DB
    azure_cosmos_endpoint: str = ""
    azure_cosmos_gremlin_endpoint: str = ""

    # AI Vision
    azure_vision_endpoint: str = ""

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_gpt_deployment: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"

    # AI Search
    azure_search_endpoint: str = ""

    # SignalR
    azure_signalr_hostname: str = ""

    # App Insights
    applicationinsights_connection_string: str = ""

    # Entra ID Auth
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_api_scope: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
