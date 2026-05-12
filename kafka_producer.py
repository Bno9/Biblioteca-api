try:
    from kafka import KafkaProducer
except Exception as exc:
    raise RuntimeError("kafka-python não está disponível. Rode `poetry add kafka-python` e reconstrua a imagem. Erro original: " + str(exc))

import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")

producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        # pass bootstrap_servers as a list for clarity
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return producer

def enviar_evento_kafka(topico: str, evento: dict):
    producer = get_kafka_producer()
    producer.send(topico, evento)
    producer.flush()