from pydantic import BaseModel, Field

class Cycle(BaseModel):
    number: int = Field(description="Cycle number, e.g. 1 for CICLO 01")
    courses: list[str] = Field(description="Course names exactly as written in the document")

class Mesh(BaseModel):
    career: str = Field(description="Career name as written in the document")
    university: str = Field(description="University name or acronym shown in the document")
    cycles: list[Cycle] = Field(description="Every cycle in the curriculum, in order")
