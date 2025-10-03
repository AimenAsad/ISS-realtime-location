from kafka import KafkaProducer
import requests
import json
import time
import logging

# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ISS_Producer")

# --------------------------
# Kafka Producer Setup
# --------------------------
TOPIC_NAME = 'iss_realtime_location'
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

logger.info(f"Kafka producer connected. Sending data to topic: {TOPIC_NAME}")

# --------------------------
# ISS API URL
# --------------------------
API_URL = "http://api.open-notify.org/iss-now.json"

# --------------------------
# Produce Messages
# --------------------------
while True:
    try:
        res = requests.get(API_URL)
        data = res.json()

        # Produce message to Kafka
        producer.send(TOPIC_NAME, value=data)
        producer.flush()
        logger.info(f"Produced: {data}")

    except Exception as e:
        logger.error(f"Error fetching or producing data: {e}")

    time.sleep(1)  # fetch every 1 second
