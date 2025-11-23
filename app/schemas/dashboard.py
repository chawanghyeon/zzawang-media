from typing import List

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_submissions: int
    average_score: float
    top_mistakes: List[str]
