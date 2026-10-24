from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

class SyllabusRecord(Base):
    """A syllabus a user already uploaded, so they never have to upload it again."""
    __tablename__ = "syllabi"
    # One syllabus per user and course: uploading it again replaces the old one
    __table_args__ = (UniqueConstraint("user_id", "course"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course: Mapped[str] = mapped_column(String(150))  # The mesh's spelling of the course name
    # The whole extracted Syllabus; JSONB in PostgreSQL, plain JSON elsewhere (e.g. SQLite in tests)
    data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
