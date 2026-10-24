from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

class StudyMaterialRecord(Base):
    """Generated Markdown for one topic, so each topic is paid for only once per user."""
    __tablename__ = "study_materials"
    # The database itself forbids saving the same topic twice for a user
    __table_args__ = (UniqueConstraint("user_id", "topic_hash"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course: Mapped[str] = mapped_column(String(150))
    unit: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(Text)
    # sha256 of everything that shapes the material (prompt version + prompt inputs): 64 hex chars
    topic_hash: Mapped[str] = mapped_column(String(64))
    markdown: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
