import uuid
from datetime import date, datetime, timezone

from sqlalchemy import String, Integer, DateTime, Date, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIPick(Base):
    __tablename__ = "ai_picks"
    __table_args__ = (
        UniqueConstraint("city_id", "pick_date", "pick_type", "rank", name="uq_pick_city_date_type_rank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id"), index=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id")
    )
    pick_date: Mapped[date] = mapped_column(Date, index=True)
    pick_type: Mapped[str] = mapped_column(String(50))  # top_pick, concerts, restaurants, etc.
    rank: Mapped[int] = mapped_column(Integer)
    ai_blurb: Mapped[str] = mapped_column(Text)
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    city: Mapped["City"] = relationship(back_populates="ai_picks")
    event: Mapped["Event"] = relationship(back_populates="ai_picks")
