from dataclasses import dataclass
from typing import Optional, Dict



@dataclass
class Relation:
    name: str
    properties: Optional[Dict[str, str | int]] = None