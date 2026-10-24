from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import SyllabusRecord
from ..schemas import Syllabus

def save_syllabus(db: Session, user_id: int, syllabus: Syllabus) -> None:
    """Save the user's syllabus for its course, replacing the one they uploaded before."""
    data = syllabus.model_dump()
    record = _find(db, user_id, syllabus.course)
    if record is None:
        db.add(SyllabusRecord(user_id=user_id, course=syllabus.course, data=data))
    else:
        record.data = data
    try:
        db.commit()
    except IntegrityError:
        # Two uploads of the same course arrived at once and the other one saved first: update it
        db.rollback()
        _find(db, user_id, syllabus.course).data = data
        db.commit()

def list_syllabi(db: Session, user_id: int, courses: Sequence[str]) -> list[Syllabus]:
    """The user's saved syllabi for the given courses (e.g. the courses of one cycle)."""
    records = db.scalars(
        select(SyllabusRecord)
        .where(SyllabusRecord.user_id == user_id, SyllabusRecord.course.in_(courses))
        .order_by(SyllabusRecord.course)
    )
    return [Syllabus.model_validate(record.data) for record in records]

def _find(db: Session, user_id: int, course: str) -> SyllabusRecord | None:
    return db.scalar(
        select(SyllabusRecord).where(SyllabusRecord.user_id == user_id, SyllabusRecord.course == course)
    )
