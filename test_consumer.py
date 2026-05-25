# test_consumer.py
import os
import json
from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()

broker = os.getenv("REDPANDA_BROKER_LOCAL", "localhost:9092")
print(f"Connecting to: {broker}")

c = Consumer({
    "bootstrap.servers":     broker,
    "group.id":              "test-group-throwaway",
    "auto.offset.reset":     "earliest",
    "broker.address.family": "v4",
})
c.subscribe(["raw-media-events"])

print("Consumer created. Reading messages...")
count = 0
while count < 5:
    msg = c.poll(timeout=10.0)
    if msg is None:
        print("No message received in 10s window.")
        break
    if msg.error():
        print(f"Error: {msg.error()}")
        break
    val = json.loads(msg.value().decode("utf-8"))
    count += 1
    print(f"[{count}] {val.get('source_domain')} — {val.get('title','')[:60]}")

print(f"Done. Read {count} messages.")
c.close()