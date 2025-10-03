import json
import os
import logging
import snowflake.connector
from kafka.errors import TopicAlreadyExistsError
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic


# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ISS_Consumer")

# --------------------------
# Kafka Setup
# --------------------------
TOPIC_NAME = 'iss_realtime_location'
BOOTSTRAP_SERVERS = 'localhost:9092'

# Admin client to create topic if it doesn't exist
admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
try:
    topic_list = [NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    logger.info(f"Kafka topic '{TOPIC_NAME}' created.")
except TopicAlreadyExistsError:
    logger.info(f"Kafka topic '{TOPIC_NAME}' already exists.")
except Exception as e:
    logger.error(f"Error creating Kafka topic: {e}")

# Consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='iss_snowflake_loader',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
logger.info(f"Kafka consumer connected and subscribed to topic: {TOPIC_NAME}")

# --------------------------
# Snowflake Setup
# --------------------------
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE"),
    autocommit=True
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS iss_realtime_location (
    message STRING,
    longitude STRING,
    latitude STRING,
    timestamp STRING
)
""")
logger.info("Snowflake table 'iss_realtime_location' is ready.")

# --------------------------
# Consume & Insert
# --------------------------
logger.info("✅ Consumer is now listening for ISS data...")

try:
    for msg in consumer:
        data = msg.value
        try:
            cursor.execute(
                """
                INSERT INTO iss_realtime_location (message, longitude, latitude, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    data.get('message'),
                    data['iss_position']['longitude'],
                    data['iss_position']['latitude'],
                    str(data.get('timestamp'))
                )
            )
            logger.info(f"Inserted into Snowflake: {data}")
        except Exception as e:
            logger.error(f"Failed to insert data into Snowflake: {e} | Data: {data}")

except KeyboardInterrupt:
    logger.info("Consumer stopped by user.")

finally:
    cursor.close()
    conn.close()
    logger.info("Snowflake connection closed. Consumer exiting.")
