from dataclasses import dataclass


@dataclass
class Experience:
    company: str
    position: str
    start_date: str
    end_date: str
    location: str
