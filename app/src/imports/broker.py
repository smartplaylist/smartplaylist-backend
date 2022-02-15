import pika

"""broker" is a RabbitMQ service name from stack.yml file"""
connection = pika.BlockingConnection(pika.ConnectionParameters("broker"))


def create_channel(name):
    """Creates RabbitMQ channel"""
    channel = connection.channel()
    channel.queue_declare(queue=name)
    channel.basic_qos(prefetch_count=1)

    return channel


def close_connection():
    connection.close()
