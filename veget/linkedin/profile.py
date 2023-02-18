from dataclasses import dataclass
from typing import List

from .experience import Experience


@dataclass
class Profile:
    name: str
    experiences: List[Experience]
