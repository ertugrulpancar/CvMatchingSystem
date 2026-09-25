import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AnalysisModel(Base):
    __tablename__ = "analyses"

    # server_default: bu sütunların değerini biz değil Postgres üretir
    # (migration'daki `default gen_random_uuid()`/`default now()` ile
    # eşleşir). server_default olmadan SQLAlchemy sütunu INSERT'e NULL
    # olarak gönderir ve NOT NULL kısıtlaması hata verir.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    job_title: Mapped[str | None] = mapped_column(Text)
    company_name: Mapped[str | None] = mapped_column(Text)
    job_text: Mapped[str] = mapped_column(Text, nullable=False)
    cv_source: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    output_language: Mapped[str] = mapped_column(Text, nullable=False)
    matcher: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int] = mapped_column(nullable=False)

    items: Mapped[list["AnalysisItemModel"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="AnalysisItemModel.position",
    )

    __table_args__ = (Index("analyses_user_created_idx", "user_id", created_at.desc()),)


class AnalysisItemModel(Base):
    __tablename__ = "analysis_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    analysis: Mapped["AnalysisModel"] = relationship(back_populates="items")

    __table_args__ = (Index("analysis_items_analysis_idx", "analysis_id"),)
