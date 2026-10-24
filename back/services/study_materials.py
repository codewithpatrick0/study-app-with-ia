import hashlib
import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import StudyMaterialRecord
from ..schemas import StudyMaterialRequest

def material_hash(request: StudyMaterialRequest, prompt_version: int) -> str:
    """Fingerprint of everything that shapes the material; bumping prompt_version invalidates old ones."""
    payload = json.dumps(
        {"prompt_version": prompt_version, **request.model_dump()},
        sort_keys=True,  # Same data → same text → same hash, whatever the key order
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def find_material(db: Session, user_id: int, topic_hash: str) -> str | None:
    """The user's saved Markdown for this topic, or None if it was never generated."""
    return db.scalar(
        select(StudyMaterialRecord.markdown).where(
            StudyMaterialRecord.user_id == user_id,  # Always scoped to the logged-in user
            StudyMaterialRecord.topic_hash == topic_hash,
        )
    )

def save_material(
    db: Session, user_id: int, topic_hash: str, request: StudyMaterialRequest, markdown: str
) -> None:
    """Save generated Markdown; if the same topic was saved meanwhile, keep that one."""
    db.add(StudyMaterialRecord(
        user_id=user_id,
        course=request.course,
        unit=request.unit,
        topic=request.topic,
        topic_hash=topic_hash,
        markdown=markdown,
    ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # A parallel request for the same topic saved first; nothing to do
