from kafka import KafkaConsumer, consumer
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
import os
import datetime

KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')

# cloud_config= {
#     'secure_connect_bundle': 'secure-connect-driver.zip'
# }
# auth_provider = PlainTextAuthProvider(os.environ.get("ASTRA_ID"), os.environ.get("ASTRA_KEY"))
# cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)

cluster = Cluster(contact_points=['127.0.0.1'],
                  port=9042)
session = cluster.connect()
print("Cassandra connected")


def consume_kafka():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='group-0',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    return consumer


for item in consume_kafka():
    event = item.value
    print(event)

    session.execute(
        f"""
        INSERT INTO actions.{KAFKA_TOPIC} (user_id, anime_id, happened_at)
        VALUES (%s, %s, %s)
        """,
        (
            int(event['user_id']),
            int(event['anime_id']),
            datetime.datetime.fromtimestamp(event['happened_at'])
        )
    )
