from utils.logger import make_log
from kafka.services import KafkaProducerSingleton

kafka_producer = KafkaProducerSingleton()


def signal_handler(signum, frame):
    make_log("KAFKA", 20, "workflow.log", f"Signal received: {signum}")
    make_log("KAKFA", 20, "workflow.log", "Gracefully shutting down kafka producer...")

    kafka_producer.flush()
    kafka_producer.close()
