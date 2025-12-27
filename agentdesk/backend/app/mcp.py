import httpx
from fastapi import HTTPException

MCP_SOURCES = [
    "https://api.github.com/search/repositories?q=topic:mcp",
    "https://mcp.so/api/search",
    "https://glama.ai/mcp/reference/api/search",
]

async def search_mcp(query: str):
    results = []
    async with httpx.AsyncClient() as client:
        for source in MCP_SOURCES:
            try:
                response = await client.get(f"{source}?q={query}")
                response.raise_for_status()
                results.append(response.json())
            except httpx.HTTPStatusError as exc:
                raise HTTPException(status_code=exc.response.status_code, detail=f"Error connecting to {source}")
    return results
