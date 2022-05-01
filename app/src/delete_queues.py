import os
import queue
import sys

import pika

from imports.logging import get_logger


def main():
    log = get_logger(os.path.basename(__file__))
    connection = pika.BlockingConnection(pika.ConnectionParameters("broker"))
    channel = connection.channel()

    queues = ["albums", "artists", "related_artists", "tracks"]

    for i in queues:
        log.info(f"Deleting queue {i}")
        channel.queue_delete(queue=i)

    connection.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
