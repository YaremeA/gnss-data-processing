import csv
from datetime import datetime
from pathlib import Path
from gnss_application.gnss_data import GNSSData

class GNSSLogger:

    def __init__(
        self,
        csv_filename: str = "gnss_data_log.csv",
        raw_filename: str = "nmea_raw_log.txt",
    ) -> None:
        self.csv_file = Path(csv_filename)
        self.raw_file = Path(raw_filename)
        self.create_csv_file()
    def create_csv_file(self) -> None:
        if self.csv_file.exists():
            return
        with open(self.csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "local_timestamp",
                    "unix_timestamp",
                    "sentence_type",
                    "fix_status",
                    "fix_quality",
                    "latitude",
                    "longitude",
                    "satellites",
                    "hdop",
                    "altitude_m",
                    "speed_kmh",
                    "course_deg",
                    "data_valid",
                    "processing_delay_ms",
                    "raw_nmea",
                ]
            )
    def save_csv(self, data: GNSSData) -> None:
        with open(self.csv_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    data.local_timestamp,
                    data.unix_timestamp,
                    data.sentence_type,
                    data.fix_status,
                    data.fix_quality,
                    data.latitude,
                    data.longitude,
                    data.satellites,
                    data.hdop,
                    data.altitude_m,
                    data.speed_kmh,
                    data.course_deg,
                    data.data_valid,
                    data.processing_delay_ms,
                    data.raw_nmea,
                ]
            )
    def save_raw(self, raw_nmea: str) -> None:
        with open(self.raw_file, "a", encoding="utf-8") as file:
            file.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} {raw_nmea}\n"
            )
