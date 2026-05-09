from pydantic import BaseModel
from typing import List, Optional


class CompareDataResponse(BaseModel):
    chart1: dict
    chart2: dict
    chart3: dict
    chart4: dict
    generated_at: str


class HongliHealthResponse(BaseModel):
    status: str
    time: str