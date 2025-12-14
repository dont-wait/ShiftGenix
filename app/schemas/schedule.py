from pydantic import BaseModel
from typing import List, Dict

class Staff(BaseModel):
    id: int
    name: str
    role: str

class Shift(BaseModel):
    id: int
    name: str

class ScheduleRequest(BaseModel):
    staff: List[Staff]
    shifts: List[Shift]
    days: int

class ScheduleResponse(BaseModel):
    schedule: Dict[str, Dict[str, str]]
    fitness_score: float
