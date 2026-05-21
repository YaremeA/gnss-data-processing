import json
import time
import uuid
import threading
import msgpack
import pandas as pd
import paho.mqtt.client as mqtt
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

N = 300
REQUEST_TOPIC_PREFIX = "gnss/request/"
RESPONSE_TOPIC_PREFIX = "gnss/response/"

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
    "altitude": 545.4,
}

responses = {}
response_events = {}
def build_json_payload() -> bytes:
    return json.dumps(parsed_data).encode("utf-8")
def build_toon_payload() -> bytes:
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
  
    return toon_data.encode("utf-8")
def build_msgpack_payload() -> bytes:
    return msgpack.packb(parsed_data, use_bin_type=True)
payload_builders = {
    "json": build_json_payload,
    "toon": build_toon_payload,
    "msgpack": build_msgpack_payload,
}

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[CLIENT] Connected to MQTT broker")
    client.subscribe(RESPONSE_TOPIC_PREFIX + "#")
def on_message(client, userdata, message):
    try:
        request_id = message.topic.split("/")[-1]
        response = json.loads(message.payload.decode("utf-8"))
        responses[request_id] = response
        if request_id in response_events:
            response_events[request_id].set()
    except Exception as error:
        print(f"[CLIENT] Response processing error: {error}")
def send_and_measure(client, data_format: str, timeout: float = 2.0) -> dict:
    request_id = str(uuid.uuid4())
    response_event = threading.Event()
    response_events[request_id] = response_event
    topic = f"{REQUEST_TOPIC_PREFIX}{data_format}/{request_id}"
    payload = payload_builders[data_format]()
    start_time = time.perf_counter()
    client.publish(topic, payload, qos=0)
    received = response_event.wait(timeout=timeout)
    end_time = time.perf_counter()
    total_delay_ms = (end_time - start_time) * 1000
    response = responses.get(request_id)
    server_processing_time = None
    status = "timeout"

    if received and response is not None:
        status = response.get("status")
        server_processing_time = response.get("server_processing_time_ms")
    response_events.pop(request_id, None)
    responses.pop(request_id, None)
    return {
        "format": data_format,
        "request_id": request_id,
        "total_delay_ms": total_delay_ms,
        "server_processing_time_ms": server_processing_time,
        "status": status,
    }
  
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)
    results = []
    for data_format in payload_builders:
        print(f"Testing MQTT format: {data_format}")
        for i in range(N):
            result = send_and_measure(client, data_format)
            result["iteration"] = i + 1
            results.append(result)
    client.loop_stop()
    client.disconnect()
    df = pd.DataFrame(results)
    df.to_csv("mqtt_latency_results.csv", index=False, encoding="utf-8-sig")

    summary = df[df["status"] == "ok"].groupby("format")["total_delay_ms"].agg(
        mean_delay_ms="mean",
        min_delay_ms="min",
        max_delay_ms="max",
        std_delay_ms="std",
    )
  
    summary.to_csv("mqtt_latency_summary.csv", encoding="utf-8-sig")
    print("\nMQTT latency summary:")
    print(summary)
  
if __name__ == "__main__":
    main()
