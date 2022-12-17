from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    day_of_week: str
    date: datetime
    shift: str
