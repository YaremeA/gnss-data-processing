import time
from datetime import datetime
from gnss_application.gnss_data import GNSSData

class NMEAParser:
    @staticmethod
    def get_sentence_type(nmea_line: str | None) -> str | None:
        if nmea_line is None or not nmea_line.startswith("$"):
            return None
        header = nmea_line.split(",")[0]
        if len(header) < 6:
            return None
        return header[-3:]
    @staticmethod
    def validate_checksum(nmea_line: str | None) -> bool:
        if nmea_line is None:
            return False
        if not nmea_line.startswith("$") or "*" not in nmea_line:
            return False
        try:
            data, received_checksum = nmea_line[1:].split("*", 1)
            received_checksum = received_checksum[:2]
            calculated_checksum = 0
            for char in data:
                calculated_checksum ^= ord(char)
            return calculated_checksum == int(received_checksum, 16)
        except ValueError:
            return False
    @staticmethod
    def nmea_to_decimal(coord: str | None, direction: str | None) -> float | None:

        if not coord or not direction:
            return None
        try:
            raw = float(coord)
            degrees = int(raw // 100)
            minutes = raw - degrees * 100
            decimal = degrees + minutes / 60
            if direction in ["S", "W"]:
                decimal = -decimal
            return decimal
        except ValueError:
            return None
    @staticmethod
    def safe_float(value: str | None) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except ValueError:
            return None
    @staticmethod
    def safe_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def knots_to_kmh(speed_knots: str | None) -> float | None:
        speed = NMEAParser.safe_float(speed_knots)
        if speed is None:
            return None
        return speed * 1.852
    def parse(self, nmea_line: str) -> GNSSData | None:
        start_time = time.perf_counter()
        if not self.validate_checksum(nmea_line):
            return None
        sentence_type = self.get_sentence_type(nmea_line)
        if sentence_type == "GGA":
            result = self.parse_gga(nmea_line)
        elif sentence_type == "RMC":
            result = self.parse_rmc(nmea_line)
        else:
            result = self.parse_basic(nmea_line)
        if result is not None:
            end_time = time.perf_counter()
            result.processing_delay_ms = (end_time - start_time) * 1000
        return result
    def parse_basic(self, nmea_line: str) -> GNSSData:
        sentence_type = self.get_sentence_type(nmea_line) or "UNKNOWN"
        return GNSSData(
            local_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            unix_timestamp=time.time(),
            sentence_type=sentence_type,
            raw_nmea=nmea_line,
        )

    def parse_gga(self, nmea_line: str) -> GNSSData | None:
        parts = nmea_line.split(",")
        if len(parts) < 10:
            return None
        fix_quality = self.safe_int(parts[6])
        fix_descriptions = {
            0: "NO FIX",
            1: "GPS FIX",
            2: "DGPS FIX",
            4: "RTK FIX",
            5: "RTK FLOAT",
        }
        if fix_quality is None:
            fix_status = "UNKNOWN"
        else:
            fix_status = fix_descriptions.get(fix_quality, "UNKNOWN")
        return GNSSData(
            local_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            unix_timestamp=time.time(),
            sentence_type="GGA",
            raw_nmea=nmea_line,
            fix_status=fix_status,
            fix_quality=fix_quality,
            latitude=self.nmea_to_decimal(parts[2], parts[3]),
            longitude=self.nmea_to_decimal(parts[4], parts[5]),
            satellites=self.safe_int(parts[7]),
            hdop=self.safe_float(parts[8]),
            altitude_m=self.safe_float(parts[9]),
        )

    def parse_rmc(self, nmea_line: str) -> GNSSData | None:
        parts = nmea_line.split(",")
        if len(parts) < 10:
            return None
        status = parts[2]
        data_valid = status == "A"
        return GNSSData(
            local_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            unix_timestamp=time.time(),
            sentence_type="RMC",
            raw_nmea=nmea_line,
            data_valid=data_valid,
            latitude=self.nmea_to_decimal(parts[3], parts[4]),
            longitude=self.nmea_to_decimal(parts[5], parts[6]),
            speed_kmh=self.knots_to_kmh(parts[7]),
            course_deg=self.safe_float(parts[8]),
        )
