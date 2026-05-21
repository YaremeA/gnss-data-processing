import time
import requests
import pandas as pd

URL = "http://127.0.0.1:8000/gnss/latency-test/"

N = 300

NMEA_SENTENCE = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"

parsed_data = {
    "sentence": "GPGGA",
    "utc_time": "123519",
    "latitude": 48.1173,
    "latitude_dir": "N",
    "longitude": 11.5167,
    "longitude_dir": "E",
    "fix_quality": 1,
    "satellites": 8,
    "hdop": 0.9,
    "altitude": 545.4
}

def send_raw_nmea():
    return requests.post(
        URL,
        data=NMEA_SENTENCE.encode("utf-8"),
        headers={"Content-Type": "text/plain"}
    )


def send_json():
    return requests.post(URL, json=parsed_data)
  
def send_form():
    return requests.post(
        URL,
        data=parsed_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
  
def send_multipart():
    return requests.post(
        URL,
        files={"file": ("empty.txt", "")},
        data=parsed_data
    )
  
def send_toon():
    toon_data = (
        "sentence:GPGGA\n"
        "utc_time:123519\n"
        "latitude:48.1173\n"
        "latitude_dir:N\n"
        "longitude:11.5167\n"
        "longitude_dir:E\n"
        "fix_quality:1\n"
        "satellites:8\n"
        "hdop:0.9\n"
        "altitude:545.4"
    )
    return requests.post(
        URL,
        data=toon_data.encode("utf-8"),
        headers={"Content-Type": "text/plain"}
    )
  
formats = {
    "raw_nmea": send_raw_nmea,
    "json": send_json,
    "form": send_form,
    "multipart": send_multipart,
    "toon": send_toon
}

results = []

for format_name, send_function in formats.items():
    print(f"Testing format: {format_name}")
    for i in range(N):
        start_time = time.perf_counter()
        response = send_function()
        end_time = time.perf_counter()
        total_delay_ms = (end_time - start_time) * 1000
        server_time = None
        if response.status_code == 200:
            server_time = response.json().get("server_processing_time_ms")
        results.append({
            "format": format_name,
            "iteration": i + 1,
            "total_delay_ms": total_delay_ms,
            "server_processing_time_ms": server_time,
            "status_code": response.status_code
        })
      
df = pd.DataFrame(results)

df.to_csv("latency_results.csv", index=False, encoding="utf-8-sig")

summary = df.groupby("format")["total_delay_ms"].agg(
    mean_delay_ms="mean",
    min_delay_ms="min",
    max_delay_ms="max",
    std_delay_ms="std"
)
summary.to_csv("latency_summary.csv", encoding="utf-8-sig")
print(summary)
