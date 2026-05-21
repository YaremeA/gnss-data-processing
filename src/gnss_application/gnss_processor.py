from low_level_driver.usb_com_driver import USBComDriver
from gnss_application.django_client import DjangoGNSSClient
from gnss_application.gnss_data import GNSSData
from gnss_application.gnss_logger import GNSSLogger
from gnss_application.nmea_parser import NMEAParser

class GNSSProcessor:
    ALLOWED_TYPES = {"GGA", "RMC", "GSA", "GSV", "VTG", "GLL"}

    def __init__(
        self,
        port: str | None = None,
        baudrate: int = 9600,
        enable_logging: bool = True,
        enable_django_sending: bool = True,
        django_url: str = "http://127.0.0.1:8000/gnss/receive/",
    ) -> None:

        self.driver = USBComDriver(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
        )
        self.parser = NMEAParser()
        self.logger = GNSSLogger()
        self.django_client = DjangoGNSSClient(django_url=django_url)
        self.enable_logging = enable_logging
        self.enable_django_sending = enable_django_sending
        self.last_gga_status: tuple | None = None
      
    def start(self) -> None:
        self.driver.open()
      
    def stop(self) -> None:
        self.driver.close()

    def read_raw_nmea(self) -> str | None:
        packet = self.driver.read_until(delimiter=b"\n")
        if packet is None:
            return None

        line = packet.decode("ascii", errors="replace").strip()
        if not line.startswith("$"):
            return None
        return line
      
    def read_once(self) -> GNSSData | None:
        raw_line = self.read_raw_nmea()
        if raw_line is None:
            return None
          
        sentence_type = self.parser.get_sentence_type(raw_line)
        if sentence_type not in self.ALLOWED_TYPES:
            return None
        parsed_data = self.parser.parse(raw_line)
      
        if parsed_data is None:
            return None
          
        if self.enable_logging:
            self.logger.save_raw(raw_line)
            self.logger.save_csv(parsed_data)
        return parsed_data
      
    def read_once_as_dict(self) -> dict | None:
        data = self.read_once()
        if data is None:
            return None
        return data.to_dict()
      
    def read_once_as_json(self) -> str | None:
        data = self.read_once()
        if data is None:
            return None
        return data.to_json()
      
    def print_console_status(self, data: GNSSData) -> None:

        if data.processing_delay_ms is None:
            delay_text = "N/A"
        else:
            delay_text = f"{data.processing_delay_ms:.3f}"
          
        if data.sentence_type == "GGA":
            status = (
                data.fix_status,
                data.satellites,
                data.hdop,
                data.latitude,
                data.longitude,
            )
            if status != self.last_gga_status:
                print(
                    f"[GGA] Fix: {data.fix_status} | "
                    f"Satellites: {data.satellites} | "
                    f"HDOP: {data.hdop} | "
                    f"Delay: {delay_text} ms"
                )
                if data.latitude is not None and data.longitude is not None:
                    print(
                        f"      Position: {data.latitude:.6f}, "
                        f"{data.longitude:.6f} | "
                        f"Alt: {data.altitude_m} m"
                    )
                self.last_gga_status = status
        elif data.sentence_type == "RMC" and data.data_valid:
            if data.speed_kmh is None:
                speed_text = "N/A"
         
   	    else:
                speed_text = f"{data.speed_kmh:.2f}"
            print(
                f"[RMC] Valid: {data.data_valid} | "
                f"Speed: {speed_text} km/h | "
                f"Course: {data.course_deg}"
            )
    def run_console(self) -> None:
        print("[INFO] Режим обробки GNSS-даних запущено.")
        print("[INFO] Для завершення натисніть Ctrl+C.\n")
        try:
            while True:
                data = self.read_once()
                if data is not None:
                    self.print_console_status(data)
                    if self.enable_django_sending:
                        self.django_client.send(data)
                      
        except KeyboardInterrupt:
            print("\n[INFO] Роботу зупинено користувачем.")
