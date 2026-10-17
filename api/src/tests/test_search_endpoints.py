import asyncio
import json
import os
import unittest
from datetime import date
from unittest import mock
from urllib.parse import urlsplit

# models.track builds its engine at import time; nothing connects in these tests.
for name in ("POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"):
    os.environ.setdefault(name, "unused")

import main  # noqa: E402

# Exactly what the website requests with its default form values.
WEBSITE_QUERY = (
    "?_&rel=2022-01-01&tem=80,210&pop=0,100&map=0,100&maf=1,50000000"
    "&dan=0,100&ene=0,100&spe=0,100&aco=0,100&ins=0,100&liv=0,100&val=0,100"
    "&key=any,any&order=rel,des&limit=250"
)


def request(method, url, body=None):
    """Send one request through the ASGI app, returning (status, decoded JSON).

    Starlette's TestClient cannot run on the anyio release the image resolves
    to, and this needs nothing beyond the standard library.
    """
    parts = urlsplit(url)
    payload = b"" if body is None else json.dumps(body).encode()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": parts.path,
        "raw_path": parts.path.encode(),
        "query_string": parts.query.encode(),
        "root_path": "",
        "headers": [
            (b"host", b"testserver"),
            (b"content-type", b"application/json"),
            (b"content-length", str(len(payload)).encode()),
        ],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    incoming = [{"type": "http.request", "body": payload, "more_body": False}]
    sent = []

    async def receive():
        return incoming.pop(0) if incoming else {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    asyncio.run(main.app(scope, receive, send))
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    content = b"".join(
        m.get("body", b"") for m in sent if m["type"] == "http.response.body"
    )
    return status, json.loads(content) if content else None


class SearchEndpointsTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(main, "Track")
        self.track = patcher.start().return_value
        self.addCleanup(patcher.stop)
        self.track.search.return_value = []
        self.track.count.return_value = 0

    def test_the_website_search_query_reaches_the_database_layer(self):
        status, body = request("GET", "/tracks" + WEBSITE_QUERY)

        self.assertEqual(status, 200, body)
        kwargs = self.track.search.call_args.kwargs
        self.assertEqual(kwargs["tempo"], [80, 210])
        self.assertEqual(kwargs["main_artist_followers"], [1, 50_000_000])
        self.assertEqual(kwargs["release"], [date(2022, 1, 1)])
        self.assertEqual(kwargs["key"], [0, 12])
        self.assertEqual(kwargs["limit"], 250)

    def test_the_website_count_query_reaches_the_database_layer(self):
        status, body = request("GET", "/tracks/count" + WEBSITE_QUERY)

        self.assertEqual(status, 200, body)
        self.assertEqual(body, 0)
        self.assertNotIn("limit", self.track.count.call_args.kwargs)

    def test_a_malformed_range_is_answered_with_bad_request(self):
        for query in ("?tem=abc", "?pop=90,10", "?key=1", "?rel=2022"):
            with self.subTest(query=query):
                status, _ = request("GET", "/tracks" + query)
                self.assertEqual(status, 400)
        self.track.search.assert_not_called()

    def test_a_malformed_count_query_is_answered_with_bad_request(self):
        status, _ = request("GET", "/tracks/count?maf=-5,10")

        self.assertEqual(status, 400)
        self.track.count.assert_not_called()


class SavePlaylistEndpointTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(main.playlist, "save_playlist")
        self.save_playlist = patcher.start()
        self.addCleanup(patcher.stop)

    def test_saving_passes_the_token_and_track_ids_to_spotify(self):
        self.save_playlist.return_value = {"snapshot_id": "abc"}
        track_id = "4uLU6hMCjMI75M1A2tKUQC"

        status, body = request(
            "POST", "/user/save_playlist", {"accessToken": "token", "ids": [track_id]}
        )

        self.assertEqual(status, 200, body)
        self.assertEqual(body, {"saved": True, "snapshot_id": "abc"})
        self.save_playlist.assert_called_once_with("token", [track_id], "")

    def test_an_invalid_body_never_reaches_spotify(self):
        status, _ = request(
            "POST", "/user/save_playlist", {"accessToken": "token", "ids": []}
        )

        self.assertEqual(status, 422)
        self.save_playlist.assert_not_called()

    def test_a_spotify_failure_is_reported_as_a_server_error(self):
        self.save_playlist.side_effect = RuntimeError("token expired")

        status, body = request(
            "POST",
            "/user/save_playlist",
            {"accessToken": "token", "ids": ["4uLU6hMCjMI75M1A2tKUQC"]},
        )

        self.assertEqual(status, 500)
        self.assertIn("token expired", body["detail"])


if __name__ == "__main__":
    unittest.main()
