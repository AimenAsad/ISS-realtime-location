# ISS Realtime Location Tracker 🛰️
This project tracks the **International Space Station (ISS)** in real-time, streams the location data via **Apache Kafka**, and loads it into **Snowflake** for reliable storage and analysis.<br>

The pipeline consists of two main components:
* **Producer**: Fetches live ISS coordinates from a public API and sends them continuously to a Kafka topic.
* **Consumer**: Reads messages from the Kafka topic and inserts the structured data into a Snowflake table.

---

## Features
* **Real-time Tracking**: Continuously monitors the ISS coordinates.
* **Reliable Streaming**: Uses **Apache Kafka** for robust, high-throughput data transmission.
* **Data Warehousing**: Automatic, secure storage in **Snowflake** for subsequent analysis and reporting.
* **Modular Design**: A simple, extensible pipeline built in Python.

---

## Tech Stack
* **Python 3.x**
* **Apache Kafka** (for data streaming)
* **Snowflake** (for data warehousing)
* **Python Libraries**: `requests`, `json`, `logging`, and connectors for Kafka/Snowflake.

---

## Setup Instructions

### 1. Clone the Repository
git clone [https://github.com/yourusername/iss-realtime-location.git](https://github.com/yourusername/iss-realtime-location.git)
cd iss-realtime-location

### 2. Create Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3. Set Environment Variables (Snowflake Credentials)
Create a .env file or set the following environment variables directly in your shell. These credentials are required by the consumer.py script.<br>
export SNOWFLAKE_USER="YOUR_USER"<br>
export SNOWFLAKE_PASSWORD="YOUR_PASSWORD"<br>
export SNOWFLAKE_ACCOUNT="YOUR_ACCOUNT"<br>
export SNOWFLAKE_WAREHOUSE="YOUR_WAREHOUSE"<br>
export SNOWFLAKE_DATABASE="YOUR_DATABASE"<br>
export SNOWFLAKE_SCHEMA="YOUR_SCHEMA"<br>
export SNOWFLAKE_ROLE="YOUR_ROLE"<br>

### 4. Start Kafka & Zookeeper
Start Zookeeper and the Kafka Broker in separate terminal sessions (assuming a local Kafka installation).

## Terminal 1: Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

## Terminal 2: Start Kafka Broker
bin/kafka-server-start.sh config/server.properties

### 5. Create Kafka Topic
Create the designated topic for the ISS data stream:<br>
bin/kafka-topics.sh --create \
    --topic iss_realtime_location \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1
    <br>
Running the Pipeline
1. Run Producer<br>
Run the producer script. This connects to the Open Notify API, fetches the coordinates, and publishes them to the Kafka topic.<br>
python3 producer.py

2. Run Consumer<br>
Run the consumer script in a new terminal. This subscribes to the Kafka topic, reads the data, and inserts it into Snowflake.<br>
python3 consumer.py

### Database Table Schema (Snowflake)
The target table in Snowflake must be initialized with the following structure to receive the data:<br>
Column	Type	Description<br>
message	STRING	The API status message (e.g., 'success')<br>
longitude	STRING	ISS longitude coordinate<br>
latitude	STRING	ISS latitude coordinate<br>
timestamp	STRING	The UNIX timestamp or formatted time of the record<br>


Example Output
### Producer Output:
Produced: {'iss_position': {'longitude': '50.8172', 'latitude': '50.4333'}, 'timestamp': 1759399245, 'message': 'success'}
### Consumer Output:
Inserted into Snowflake: {'message': 'success', 'longitude': '50.8172', 'latitude': '50.4333', 'timestamp': '2025-10-02 14:50:45'}


## Future Improvements
Scalability: Implement multiple Kafka partitions for higher message throughput.<br>
Data Types: Store coordinates in proper numeric types (FLOAT) in Snowflake for easier querying.<br>
Visualization: Build a real-time dashboard (e.g., using Streamlit, Dash, or Tableau) to visualize the ISS movement on a map.
