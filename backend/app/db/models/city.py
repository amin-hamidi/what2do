import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(2))
    timezone: Mapped[str] = mapped_column(String(50), default="America/Chicago")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    events: Mapped[list["Event"]] = relationship(back_populates="city")
    venues: Mapped[list["Venue"]] = relationship(back_populates="city")
    ai_picks: Mapped[list["AIPick"]] = relationship(back_populates="city")
    sports_teams: Mapped[list["SportsTeam"]] = relationship(back_populates="city")
