"""Monitor broker message count and alert when it is above given limit in a given time of day"""
import os

import pika
from smsapi.client import SmsApiPlClient
from smsapi.exception import SmsApiException

# Define your constants
HOST = os.getenv("RABBITMQ_HOSTNAME")
USERNAME = os.getenv("RABBITMQ_DEFAULT_USER")
PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS")
SMSAPI_TOKEN = os.getenv("SMSAPI_TOKEN")
NOTIFICATION_PHONE_NUMBER = os.getenv("NOTIFICATION_PHONE_NUMBER")

# Define your queues and the minimum number of messages for each
QUEUES = {"albums": 1, "artists": 0, "tracks": 1}

smsapi = SmsApiPlClient(access_token=SMSAPI_TOKEN)

credentials = pika.PlainCredentials(USERNAME, PASSWORD)  # type: ignore
params = pika.ConnectionParameters(host=HOST, credentials=credentials)  # type: ignore
connection = pika.BlockingConnection(params)
channel = connection.channel()


def check_queue_alerts(channel):
    """Checks all queues and sends an alert if a queue has too many messages."""
    for queue_name, min_messages in QUEUES.items():
        method_frame, _, _ = channel.basic_get(queue_name)
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            message_count = method_frame.message_count + 1
            if message_count > min_messages:
                send_alert(
                    f"Smartplaylist\nQueue {queue_name} has {message_count} messages."
                )


def send_sms(phone_number, message):
    """Sends an SMS to the specified phone number."""
    try:
        send_results = smsapi.sms.send(to=phone_number, message=message)
        for result in send_results:
            print(result.id, result.points, result.error)
    except SmsApiException as exception:
        print(exception.message, exception.code)


def send_alert(message):
    """Sends an alert message to the predefined phone number."""
    send_sms(NOTIFICATION_PHONE_NUMBER, message)


def main(channel):
    """main"""
    try:
        check_queue_alerts(channel)
    finally:
        connection.close()


if __name__ == "__main__":
    main(channel)
