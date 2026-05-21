import requests
from gnss_application.gnss_data import GNSSData

class DjangoGNSSClient:
    def __init__(
        self,
        django_url: str = "http://127.0.0.1:8000/gnss/receive/",
        timeout: float = 2.0,
      
    ) -> None:
        self.django_url = django_url
        self.timeout = timeout
      
    def send(self, data: GNSSData) -> bool:
      
        try:
            response = requests.post(
                self.django_url,
                json=data.to_dict(),
                timeout=self.timeout,
            )
          
            if response.status_code == 200:
                print("[DJANGO] Дані успішно надіслано.")
                return True
            print(f"[DJANGO] Помилка надсилання: {response.status_code}")
            print(response.text)
            return False
          
        except requests.RequestException as error:
            print(f"[DJANGO] Не вдалося підключитися до Django-сервера: {error}")
            return False
