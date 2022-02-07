#!/usr/bin/env python
import pika

# "broker" is a RabbitMQ service name from stack.yml file
connection = pika.BlockingConnection(pika.ConnectionParameters('broker'))
channel = connection.channel()

channel.queue_declare(queue='hello')

for count in range(5000):
    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body="Hello")

print(" [x] Sent 'Hello World!'")

connection.close()
