import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Float, Boolean, DateTime, Text, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_city_category_starts", "city_id", "category_id", "starts_at"),
        Index("ix_events_city_starts", "city_id", "starts_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id"), index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), index=True
    )
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id"), nullable=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id")
    )

    # Content
    title: Mapped[str] = mapped_column(String(500), index=True)
    slug: Mapped[str] = mapped_column(String(600))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_url: Mapped[str] = mapped_column(String(2000))

    # Timing
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Classification
    tags: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    cuisine_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Dedup
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Embedding (for RAG vector search)
    embedding = mapped_column(Vector(384), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="active", server_default="active"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    city: Mapped["City"] = relationship(back_populates="events")
    category: Mapped["Category"] = relationship(back_populates="events")
    venue: Mapped["Venue"] = relationship(back_populates="events")
    source: Mapped["Source"] = relationship(back_populates="events")
    ai_picks: Mapped[list["AIPick"]] = relationship(back_populates="event")
