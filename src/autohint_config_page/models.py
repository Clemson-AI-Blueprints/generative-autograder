from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class FileRecord:
    """Metadata about a single uploaded file."""
    name: str
    category: str
    visible_to_students: bool = True
    upload_path: Path = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "visible_to_students": self.visible_to_students,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FileRecord":
        return FileRecord(**data)
