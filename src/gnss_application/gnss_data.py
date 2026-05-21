import json

from dataclasses import dataclass, asdict

@dataclass
class GNSSData:
  
    local_timestamp: str
    unix_timestamp: float
    sentence_type: str
    raw_nmea: str
    fix_status: str | None = None
    fix_quality: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    satellites: int | None = None
    hdop: float | None = None
    altitude_m: float | None = None
    speed_kmh: float | None = None
    course_deg: float | None = None
    data_valid: bool | None = None
    processing_delay_ms: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)
      
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

