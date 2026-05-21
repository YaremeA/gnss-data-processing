import json
import time
import msgpack
import paho.mqtt.client as mqtt

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
REQUEST_TOPIC = "gnss/request/#"
RESPONSE_TOPIC_PREFIX = "gnss/response/"

def parse_toon(text: str) -> dict:
    data = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def process_payload(data_format: str, payload: bytes) -> dict:
    if data_format == "json":
        return json.loads(payload.decode("utf-8"))
    if data_format == "toon":
        return parse_toon(payload.decode("utf-8"))
    if data_format == "msgpack":
        return msgpack.unpackb(payload, raw=False)

    raise ValueError(f"Невідомий формат даних: {data_format}")
  
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[SERVER] Connected to MQTT broker")
    client.subscribe(REQUEST_TOPIC)
    print(f"[SERVER] Subscribed to topic: {REQUEST_TOPIC}")
  
def on_message(client, userdata, message):
    start_time = time.perf_counter()
  
    try:
        topic_parts = message.topic.split("/")
        data_format = topic_parts[2]
        request_id = topic_parts[3]
        decoded_data = process_payload(data_format, message.payload)
        end_time = time.perf_counter()
        server_processing_time_ms = (end_time - start_time) * 1000
        response = {
            "status": "ok",
            "request_id": request_id,
            "format": data_format,
            "server_processing_time_ms": server_processing_time_ms,
            "received_sentence": decoded_data.get("sentence"),
        }
      
    except Exception as error:
        request_id = "unknown"
        response = {
            "status": "error",
            "error": str(error),
        }
      
    response_topic = RESPONSE_TOPIC_PREFIX + request_id
    client.publish(
        response_topic,
        json.dumps(response).encode("utf-8"),
        qos=0,
    )
  
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    print("[SERVER] MQTT latency server started")
    client.loop_forever()
  
if __name__ == "__main__":
    main()
