import serial
import serial.tools.list_ports

class USBComDriver:

    DEVICE_KEYWORDS = [
        "gps",
        "gnss",
        "u-blox",
        "ublox",
        "vk-172",
        "ch340",
        "usb-serial",
        "serial",
    ]

    def __init__(
        self,
        port: str | None = None,
        baudrate: int = 9600,
        timeout: float = 1.0,
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: float = serial.STOPBITS_ONE,
    ) -> None:

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits

        self.connection: serial.Serial | None = None
        self.receive_buffer = bytearray()

    @staticmethod
    def list_ports() -> list[str]:

        ports = serial.tools.list_ports.comports()
        return [str(port.device) for port in ports]

    def find_port(self) -> str | None:

        ports = list(serial.tools.list_ports.comports())

        if not ports:
            return None

        for port in ports:
            description = str(port.description).lower()
            manufacturer = str(port.manufacturer).lower()
            full_info = description + " " + manufacturer

            for keyword in self.DEVICE_KEYWORDS:
                if keyword in full_info:
                    return str(port.device)

        return str(ports[0].device)

    def open(self) -> None:
        if self.connection is not None and self.connection.is_open:
            return
        if self.port is None:
            self.port = self.find_port()
        if self.port is None:
            raise serial.SerialException(
                "COM-порт пристрою не знайдено. Перевірте USB-підключення."
            )

        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
            )

        except serial.SerialException as error:
            raise serial.SerialException(
                f"Не вдалося відкрити COM-порт {self.port}: {error}"
            )

    def close(self) -> None:
        if self.connection is not None and self.connection.is_open:
            self.connection.close()

        self.connection = None
        self.receive_buffer.clear()

    def is_open(self) -> bool:
        return self.connection is not None and self.connection.is_open
    def read_bytes(self, size: int = 1) -> bytes:

        if not self.is_open():
            raise serial.SerialException("COM-порт не відкрито.")
        try:
            return self.connection.read(size)

        except serial.SerialException as error:
            raise serial.SerialException(
                f"Помилка читання байтів з COM-порту: {error}"
            )

    def write_bytes(self, data: bytes) -> int:
        if not self.is_open():
            raise serial.SerialException("COM-порт не відкрито.")
        try:
            return self.connection.write(data)
        except serial.SerialException as error:
            raise serial.SerialException(
                f"Помилка запису байтів у COM-порт: {error}"
            )

    def read_until(self, delimiter: bytes = b"\n", max_size: int = 1024) -> bytes | None:
        if not self.is_open():
            raise serial.SerialException("COM-порт не відкрито.")
        while True:
            chunk = self.read_bytes(1)
            if not chunk:
                return None
            self.receive_buffer.extend(chunk)
            if delimiter in self.receive_buffer:
                packet, _, remainder = self.receive_buffer.partition(delimiter)
                self.receive_buffer = bytearray(remainder)
                return bytes(packet).strip()
            if len(self.receive_buffer) > max_size:
                self.receive_buffer.clear()
                raise BufferError(
                    "Переповнення буфера приймання. Пакет перевищує допустимий розмір."
                )

    def flush_input(self) -> None:
        if not self.is_open():
            raise serial.SerialException("COM-порт не відкрито.")

        self.connection.reset_input_buffer()
        self.receive_buffer.clear()

    def flush_output(self) -> None:
        if not self.is_open():
            raise serial.SerialException("COM-порт не відкрито.")
        self.connection.reset_output_buffer()
    def __enter__(self):
        self.open()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
