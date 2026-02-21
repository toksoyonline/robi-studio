from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    student_id: int
    scenario: str = Field(min_length=3, max_length=120)
    input_score: int = Field(ge=0, le=100)


class PremiumUpdateRequest(BaseModel):
    student_id: int
    active: bool
    plan_name: str = "Pro Monthly"


class EnrollmentUpdateRequest(BaseModel):
    student_id: int
    lesson_id: int
    progress: int = Field(ge=0, le=100)
    score: int = Field(ge=0, le=100)


class LessonCreateRequest(BaseModel):
    title: str
    description: str
    is_premium: bool = False
    difficulty: str
