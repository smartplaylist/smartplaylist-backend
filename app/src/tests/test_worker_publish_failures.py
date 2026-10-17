# Copyright (c) 2022 Kuba
# ruff: noqa: PT009

import importlib
import json
import os
import unittest
from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import patch

with patch.dict(
    os.environ,
    {
        "SPOTIFY_MARKET": "US",
        "RABBITMQ_HOSTNAME": "localhost",
        "RABBITMQ_DEFAULT_USER": "guest",
        "RABBITMQ_DEFAULT_PASS": "guest",
        "SPOTIPY_CLIENT_ID": "test-client",
        "SPOTIPY_CLIENT_SECRET": "test-secret",
    },
), patch("pika.BlockingConnection"):
    get_albums = importlib.import_module("get_albums")
    get_album_details = importlib.import_module("get_album_details")
    get_related_artists = importlib.import_module("get_related_artists")

custom_decorators = importlib.import_module("imports.custom_decorators")
PUBLISH_ATTEMPTS = 2


class DatabaseUnavailableError(Exception):
    pass


class BrokerUnavailableError(Exception):
    pass


class FakeCursor:
    def __init__(self, rowcounts=(), fail_on_execute=None):
        self.rowcounts = iter(rowcounts)
        self.fail_on_execute = fail_on_execute
        self.execute_count = 0
        self.rowcount = 0

    def execute(self, *_args, **_kwargs):
        self.execute_count += 1
        if self.execute_count == self.fail_on_execute:
            raise DatabaseUnavailableError
        self.rowcount = next(self.rowcounts, 0)

    def fetchone(self):
        return (0,)

    def fetchall(self):
        return ()


class FakeConsumer:
    def __init__(self):
        self.callback = None
        self.acknowledgements = []

    def basic_qos(self, **_kwargs):
        pass

    def basic_consume(self, on_message_callback, **_kwargs):
        self.callback = on_message_callback

    def start_consuming(self):
        pass

    def basic_ack(self, delivery_tag):
        self.acknowledgements.append(delivery_tag)


class FakePublisher:
    def __init__(self):
        self.messages = []
        self.fail = False

    def basic_publish(self, **message):
        self.messages.append(message)
        if self.fail:
            raise BrokerUnavailableError


@contextmanager
def boot_worker(module, api_function, api_response, cursor):
    consumer = FakeConsumer()
    publisher = FakePublisher()
    channels = iter((consumer, publisher))
    with ExitStack() as stack:
        stack.enter_context(
            patch.object(
                module.broker,
                "create_channel",
                side_effect=lambda _name: next(channels),
            )
        )
        stack.enter_context(patch.object(module.broker, "close_connection"))
        stack.enter_context(
            patch.object(module.db, "init_connection", return_value=(object(), cursor))
        )
        stack.enter_context(patch.object(module.db, "close_connection"))
        stack.enter_context(
            patch.object(module, api_function, return_value=api_response)
        )
        module.main()
        yield consumer, publisher


@contextmanager
def boot_album_details_worker(api_response, cursor):
    consumer = FakeConsumer()
    publisher = FakePublisher()
    channels = iter((consumer, publisher))
    with ExitStack() as stack:
        stack.enter_context(
            patch.object(
                get_album_details.broker,
                "create_channel",
                side_effect=lambda _name: next(channels),
            )
        )
        stack.enter_context(patch.object(get_album_details.broker, "close_connection"))
        stack.enter_context(
            patch.object(
                get_album_details.db,
                "init_connection",
                return_value=(object(), cursor),
            )
        )
        stack.enter_context(patch.object(get_album_details.db, "close_connection"))
        stack.enter_context(
            patch.object(
                get_album_details,
                "get_albums_details",
                return_value=api_response,
            )
        )
        stack.enter_context(patch.object(get_album_details, "PREFETCH_COUNT", 1))
        get_album_details.main()
        yield consumer, publisher


def assert_publish_error(callback):
    try:
        callback()
    except BrokerUnavailableError:
        return
    raise AssertionError


ALBUM = {
    "id": "album-1",
    "name": "Album One",
    "artists": [{"id": "artist-1", "name": "Artist One"}],
    "release_date": "2024",
    "release_date_precision": "year",
    "album_group": "album",
    "album_type": "album",
    "total_tracks": 3,
}

RELATED_ARTIST = {
    "id": "related-1",
    "name": "Related Artist",
    "popularity": 10,
    "followers": {"total": 20},
    "genres": ["jazz"],
}

ALBUM_DETAILS = {
    "id": "album-details-1",
    "name": "Album Details One",
    "release_date": "2024",
    "copyrights": [],
    "popularity": 10,
    "label": "Test Label",
    "artists": [{"id": "artist-1", "name": "Artist One"}],
    "tracks": {
        "items": [
            {
                "id": "track-1",
                "name": "Track One",
                "artists": [{"name": "Artist One"}],
                "track_number": 1,
                "disc_number": 1,
                "duration_ms": 180000,
                "explicit": False,
                "preview_url": None,
            }
        ]
    },
}


class WorkerPublishFailureTests(unittest.TestCase):
    def test_album_details_publish_failure_requeues_unacked_message(self):
        response = {"albums": [ALBUM_DETAILS]}
        payload = json.dumps({"spotify_id": "album-details-1"}).encode()

        with boot_album_details_worker(response, FakeCursor((0, 1, 1))) as (
            consumer,
            publisher,
        ):
            publisher.fail = True
            assert_publish_error(
                lambda: consumer.callback(
                    consumer,
                    SimpleNamespace(delivery_tag=5, redelivered=False),
                    None,
                    payload,
                )
            )
            self.assertFalse(consumer.acknowledgements)

        with boot_album_details_worker(response, FakeCursor((0, 0, 0))) as (
            consumer,
            publisher,
        ):
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=5, redelivered=True),
                None,
                payload,
            )

        self.assertEqual(len(publisher.messages), 1)
        self.assertEqual(publisher.messages[0]["body"], "track-1")
        self.assertEqual(consumer.acknowledgements, [5])

    def test_album_details_database_error_is_logged_and_does_not_stop_consumer(
        self,
    ):
        response = {"albums": [ALBUM_DETAILS]}
        payload = json.dumps({"spotify_id": "album-details-1"}).encode()

        with patch.object(custom_decorators, "log") as log, boot_album_details_worker(
            response, FakeCursor((0, 1), fail_on_execute=3)
        ) as (consumer, publisher):
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=6, redelivered=False),
                None,
                payload,
            )

        log.exception.assert_called_once()
        self.assertEqual(publisher.messages, [])
        self.assertEqual(consumer.acknowledgements, [6])

    def test_album_publish_failure_requeues_unacked_message(self):
        cursor = FakeCursor((0, 1, 1, 0, 1, 0))
        response = {"total": 1, "items": [ALBUM], "next": None}
        payload = json.dumps(
            {"spotify_id": "artist-1", "total_albums": 0, "name": "Artist One"}
        ).encode()

        with boot_worker(get_albums, "get_artist_albums", response, cursor) as (
            consumer,
            publisher,
        ):
            publisher.fail = True
            assert_publish_error(
                lambda: consumer.callback(
                    consumer,
                    SimpleNamespace(delivery_tag=1, redelivered=False),
                    None,
                    payload,
                )
            )

            self.assertFalse(consumer.acknowledgements)
            publisher.fail = False
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=1, redelivered=True),
                None,
                payload,
            )

        self.assertEqual(len(publisher.messages), PUBLISH_ATTEMPTS)
        self.assertEqual(consumer.acknowledgements, [1])

    def test_related_artist_publish_failure_requeues_unacked_message(self):
        cursor = FakeCursor((1, 1, 0, 1))
        response = {"artists": [RELATED_ARTIST]}
        payload = json.dumps(
            {"spotify_id": "source-artist", "name": "Source Artist"}
        ).encode()

        with boot_worker(
            get_related_artists, "get_related_artists", response, cursor
        ) as (consumer, publisher):
            publisher.fail = True
            assert_publish_error(
                lambda: consumer.callback(
                    consumer,
                    SimpleNamespace(delivery_tag=2, redelivered=False),
                    None,
                    payload,
                )
            )

            self.assertFalse(consumer.acknowledgements)
            publisher.fail = False
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=2, redelivered=True),
                None,
                payload,
            )

        self.assertEqual(len(publisher.messages), PUBLISH_ATTEMPTS)
        self.assertEqual(consumer.acknowledgements, [2])

    def test_album_database_error_is_logged_and_does_not_stop_consumer(self):
        cursor = FakeCursor((1,), fail_on_execute=2)
        response = {"total": 1, "items": [ALBUM], "next": None}
        payload = json.dumps(
            {"spotify_id": "artist-1", "total_albums": 0, "name": "Artist One"}
        ).encode()

        with patch.object(custom_decorators, "log") as log, boot_worker(
            get_albums, "get_artist_albums", response, cursor
        ) as (consumer, publisher):
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=3, redelivered=False),
                None,
                payload,
            )

        log.exception.assert_called_once()
        self.assertEqual(publisher.messages, [])
        self.assertEqual(consumer.acknowledgements, [3])

    def test_related_artist_database_error_is_logged_and_does_not_stop_consumer(
        self,
    ):
        cursor = FakeCursor((1,), fail_on_execute=1)
        response = {"artists": [RELATED_ARTIST]}
        payload = json.dumps(
            {"spotify_id": "source-artist", "name": "Source Artist"}
        ).encode()

        with patch.object(custom_decorators, "log") as log, boot_worker(
            get_related_artists, "get_related_artists", response, cursor
        ) as (consumer, publisher):
            consumer.callback(
                consumer,
                SimpleNamespace(delivery_tag=4, redelivered=False),
                None,
                payload,
            )

        log.exception.assert_called_once()
        self.assertEqual(publisher.messages, [])
        self.assertEqual(consumer.acknowledgements, [4])


if __name__ == "__main__":
    unittest.main()
