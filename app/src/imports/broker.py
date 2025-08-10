import os

import pika


def get_broker_connection():
    """
    Establishes and returns a new connection to the RabbitMQ broker.

    Includes a heartbeat for connection stability. The caller is responsible
    for managing the connection lifecycle.
    """
    host = os.environ["RABBITMQ_HOSTNAME"]
    username = os.environ["RABBITMQ_DEFAULT_USER"]
    password = os.environ["RABBITMQ_DEFAULT_PASS"]

    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(
        host=host,
        credentials=credentials,
        heartbeat=600,  # Set a 10-minute heartbeat to prevent connection drops
    )

    return pika.BlockingConnection(parameters)


def create_channel(connection, queue_name):
    """
    Creates a new channel on the given connection and declares a durable queue.
    """
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return channel
