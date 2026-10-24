from pydantic import BaseModel, Field

class Unit(BaseModel):
    number: int = Field(description="Unit number, e.g. 1 for 'Unidad de aprendizaje 1'")
    title: str = Field(description="Unit title as written in the syllabus, without trailing periods")
    topics: list[str] = Field(description="Every topic of the unit's 'Temario', one per bullet, exactly as written")

class Syllabus(BaseModel):
    course: str = Field(description="Course name as written in the syllabus, without the course code")
    course_achievement: str = Field(description="The course's general learning outcome ('Logro general de aprendizaje')")
    units: list[Unit] = Field(description="Every learning unit of the course, in order")

class SyllabusResult(BaseModel):
    """What Claude returns: lets it say 'this is not a syllabus' instead of inventing one."""
    is_syllabus: bool = Field(description="True only if the document is a course syllabus")
    syllabus: Syllabus | None = Field(description="The extracted syllabus, or null when is_syllabus is false")
