from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ConversionTaskEntity:
    id: Optional[int]
    filename: str
    source_format: str
    target_format: str
    bitrate: int
    channels: int
    status: str
    created_at: Optional[datetime] = None