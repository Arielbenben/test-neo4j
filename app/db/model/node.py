from dataclasses import dataclass
from typing import Optional



@dataclass
class Node:
    label: str
    id: Optional[str] = None