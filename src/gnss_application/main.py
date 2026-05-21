import serial
from gnss_application.gnss_processor import GNSSProcessor

def main() -> None:
    print("==============================================")
    print(" GNSS Data Processing Application")
    print(" USB-COM Driver + NMEA Parser + Logger + Django")
    print("==============================================\n")
  
    processor = GNSSProcessor(
        port=None,
        baudrate=9600,
        enable_logging=True,
        enable_django_sending=True,
        django_url="http://127.0.0.1:8000/gnss/receive/",
    )
  
    try:
        processor.start()
        processor.run_console()
      
    except serial.SerialException as error:
        print(f"[ERROR] Помилка роботи з COM-портом: {error}")
        print("[HELP] Перевірте підключення GNSS-приймача або драйвер USB-COM.")
      
    except BufferError as error:
        print(f"[ERROR] Помилка буфера: {error}")
      
    finally:
        processor.stop()
        print("[INFO] Ресурси звільнено.")
      
if __name__ == "__main__":
    main()
