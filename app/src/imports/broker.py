import os
import pika

host = os.environ["RABBITMQ_HOSTNAME"]
username = os.environ["RABBITMQ_DEFAULT_USER"]
password = os.environ["RABBITMQ_DEFAULT_PASS"]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host, credentials=pika.PlainCredentials(username, password)
    )
)


def create_channel(name):
    """Creates RabbitMQ channel"""
    channel = connection.channel()
    channel.queue_declare(queue=name, durable=True)
    channel.basic_qos(prefetch_count=1)

    return channel


def close_connection():
    connection.close()
