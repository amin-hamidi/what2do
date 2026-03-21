from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.db.models.city import City
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/{city_slug}/chat", response_model=ChatResponse)
async def chat(
    city_slug: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    # TODO: Implement RAG-based chat with Anthropic API.
    # This will embed the user query, search events via vector similarity,
    # and pass matched events as context to Claude for a natural language response.

    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    return ChatResponse(
        message=(
            f"Thanks for your question about things to do in {city.name}! "
            "Chat functionality is coming soon. In the meantime, try browsing "
            "events or checking out today's AI picks."
        ),
        events=[],
    )
