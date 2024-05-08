import os
import json
from confluent_kafka import Consumer, KafkaError, KafkaException
from dataclasses import dataclass

from utils.logger import make_log
from database.models import User
from database.models import Queue


@dataclass
class KafkaQueueMessage:
    user_id: int
    asset_id: int
    model_type_id: int


TOPIC = os.getenv("MODEL_QUEUE_TRAIN_TOPIC")

def get_consumer():
    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVER"),
            "group.id": os.getenv("KAFKA_GROUP_ID"),
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe(os.getenv("MODEL_QUEUE_TRAIN_TOPIC"))
    return consumer


async def queue_consumer_loop():
    try:
        with get_consumer() as consumer:
            while True:
                msg = consumer.poll()
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    make_log(
                        "KAFKA_CONSUMER",
                        40,
                        "models_workflow.log",
                        f"Kafka consumer error: {msg.error()}",
                    )
                    break

                try:
                    data = KafkaQueueMessage(
                        **json.loads(msg.value().decode("utf-8")))
                except json.JSONDecodeError:
                    make_log(
                        "KAFKA_CONSUMER",
                        40,
                        "models_workflow.log",
                        "Error decoding JSON request data",
                    )
                    continue

                user_id = data.user_id
                asset_id = data.asset_id
                model_type_id = data.model_type_id

                priority = await User.get(id=user_id).priority

                try:
                    await Queue(
                        user=user_id,
                        asset_id=asset_id,
                        model_type_id=model_type_id,
                        priority=priority,
                    ).save()
                except Exception as e:
                    make_log(
                        "KAFKA_DB",
                        40,
                        "models_workflow.log",
                        f"Error creating Queue object: {str(e)}",
                    )
                    continue

                consumer.commit(msg)
    except (
        KafkaException
    ) as ke:  # Propagate this error to the caller whenever I implement it
        make_log(
            "KAFKA_CONSUMER",
            40,
            "models_workflow.log",
            f"Error getting Kafka consumer: {str(ke.args[0])}",
        )


def delivery_callback(err, msg):
    if err:
        make_log(
            "KAFKA_MODEL",
            40,
            "kafka_workflow.log",
            f"ERROR: Message delivery failed: {err}",
        )
    else:
        make_log(
            "KAFKA_MODEL",
            20,
            "kafka_workflow.log",
            f"Produced event to topic {msg.topic()}, key = {msg.key().decode('utf-8')}, value = {msg.value().decode('utf-8')}",
        )
