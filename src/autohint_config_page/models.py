from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class FileRecord:
    """Metadata about a single uploaded file."""
    name: str
    category: str
    visible_to_students: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FileRecord":
        return FileRecord(**data)
