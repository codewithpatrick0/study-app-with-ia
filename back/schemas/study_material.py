from pydantic import BaseModel, ConfigDict, Field

class StudyMaterialRequest(BaseModel):
    """One topic to generate material for; the text comes from the mesh and the syllabus."""
    model_config = ConfigDict(str_strip_whitespace=True)

    # Limits keep the prompt (and what each call costs) bounded
    career: str = Field(min_length=1, max_length=150)
    course: str = Field(min_length=1, max_length=150)
    unit: str = Field(min_length=1, max_length=200)
    topic: str = Field(min_length=1, max_length=1000)
    course_achievement: str | None = Field(default=None, max_length=1000)

class StudyMaterial(BaseModel):
    """The generated study material, ready to render."""
    markdown: str
