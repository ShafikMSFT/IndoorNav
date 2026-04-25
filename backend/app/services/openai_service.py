"""Azure OpenAI service — destination parsing and direction generation."""

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.config import get_settings


def _get_client() -> AzureOpenAI:
    settings = get_settings()
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2024-08-01-preview",
    )


async def parse_destination(user_query: str, available_pois: list[dict]) -> dict:
    """Use GPT-4o to extract the destination entity from natural language."""
    settings = get_settings()
    client = _get_client()

    poi_list = "\n".join(
        f"- {p['name']}: {p['description']}" for p in available_pois
    )

    response = client.chat.completions.create(
        model=settings.azure_openai_gpt_deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an indoor navigation assistant. "
                    "The user wants to go somewhere inside a building. "
                    "Extract the destination from their message and match it "
                    "to one of the known Points of Interest (POIs). "
                    "If unsure, return the top 3 candidates.\n\n"
                    f"Known POIs:\n{poi_list}"
                ),
            },
            {"role": "user", "content": user_query},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    import json
    return json.loads(response.choices[0].message.content)


async def generate_directions(path_nodes: list[dict]) -> list[str]:
    """Convert a sequence of graph nodes into human-friendly directions."""
    settings = get_settings()
    client = _get_client()

    node_desc = "\n".join(
        f"Step {i+1}: Node '{n.get('label', n['id'])}' — {n.get('caption', '')}"
        for i, n in enumerate(path_nodes)
    )

    response = client.chat.completions.create(
        model=settings.azure_openai_gpt_deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an indoor navigation assistant. "
                    "Given a sequence of locations along a path, "
                    "generate clear, concise turn-by-turn walking directions. "
                    "Use landmarks and visual cues mentioned in node descriptions."
                ),
            },
            {
                "role": "user",
                "content": f"Generate walking directions for this path:\n{node_desc}",
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip().split("\n")


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for text (POI search)."""
    settings = get_settings()
    client = _get_client()

    response = client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=text,
    )

    return response.data[0].embedding
