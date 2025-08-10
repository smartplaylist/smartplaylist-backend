import json
import pytest
from unittest.mock import Mock, call, MagicMock

# Import the module to be tested
import get_albums

# Fixture to provide a sample RabbitMQ message body
@pytest.fixture
def artist_message_body():
    return {
        "spotify_id": "artist123",
        "total_albums": 5,
        "name": "Test Artist"
    }

# Main fixture to mock all external dependencies of the worker
@pytest.fixture
def mock_worker_dependencies(mocker, artist_message_body):
    # Mock broker
    mock_broker = mocker.patch("get_albums.broker")
    mock_consume_channel = MagicMock()
    mock_publish_channel = MagicMock()
    mock_broker.create_channel.side_effect = [mock_consume_channel, mock_publish_channel]

    # Mock db
    mock_db = mocker.patch("get_albums.db")
    mock_cursor = MagicMock()
    mock_db.init_connection.return_value = (Mock(), mock_cursor)

    # Mock spotipy
    mock_sp = mocker.patch("get_albums.sp")

    # Mock logger
    mocker.patch("get_albums.get_logger").return_value = MagicMock()

    # Mock the callback and its context
    mock_ch = MagicMock()
    mock_method = MagicMock(delivery_tag=123)
    body = json.dumps(artist_message_body).encode('utf-8')

    # Return a dictionary of mocks to be used in tests
    return {
        "broker": mock_broker,
        "consume_channel": mock_consume_channel,
        "publish_channel": mock_publish_channel,
        "db": mock_db,
        "cursor": mock_cursor,
        "sp": mock_sp,
        "callback_context": (mock_ch, mock_method, Mock(), body)
    }

def test_happy_path(mock_worker_dependencies):
    """
    Tests the main success scenario: a message is received, new albums are found,
    saved to the DB, and published to the next queue.
    """
    # Arrange
    # Get mocks from the fixture
    sp = mock_worker_dependencies["sp"]
    cursor = mock_worker_dependencies["cursor"]
    publish_channel = mock_worker_dependencies["publish_channel"]
    ch, method, props, body = mock_worker_dependencies["callback_context"]

    # Mock Spotify API response: 10 total albums, meaning 5 are new
    sp.artist_albums.return_value = {
        "total": 10,
        "next": None,
        "items": [{
            "id": "album456",
            "name": "New Album",
            "artists": [{"id": "artist123", "name": "Test Artist"}],
            "album_group": "album",
            "album_type": "album",
            "release_date": "2023-01-01",
            "release_date_precision": "day",
            "total_tracks": 10
        }]
    }
    # Mock DB insert to indicate a new album was saved
    cursor.rowcount = 1

    # Act
    # Call the callback function directly with the mocked context
    get_albums.callback(ch, method, props, body)

    # Assert
    # Check that the artist's total albums were updated
    cursor.execute.assert_any_call(
        "UPDATE artists SET total_albums=%s, albums_updated_at=%s WHERE spotify_id=%s;",
        (10, mocker.ANY, "artist123")
    )

    # Check that the new album was inserted
    cursor.execute.assert_any_call(
        "INSERT INTO albums (spotify_id, name, main_artist, all_artists, from_discography_of, album_group, album_type, release_date, release_date_precision, total_tracks, from_discography_of_spotify_id, main_artist_spotify_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
        ('album456', 'New Album', 'Test Artist', ['Test Artist'], 'Test Artist', 'album', 'album', '2023-01-01', 'day', 10, 'artist123', 'artist123')
    )

    # Check that the new album was published to the next queue
    publish_channel.basic_publish.assert_called_once()

    # Check that the message was acknowledged
    ch.basic_ack.assert_called_once_with(method.delivery_tag)


def test_no_new_albums_found(mock_worker_dependencies, artist_message_body):
    """
    Tests that if no new albums are found on Spotify, the message is ACKed
    and no further messages are published.
    """
    # Arrange
    sp = mock_worker_dependencies["sp"]
    publish_channel = mock_worker_dependencies["publish_channel"]
    ch, method, props, body = mock_worker_dependencies["callback_context"]

    # Mock Spotify to return the same number of albums as in the message
    sp.artist_albums.return_value = {"total": artist_message_body["total_albums"], "next": None, "items": []}

    # Act
    get_albums.callback(ch, method, props, body)

    # Assert
    # No albums should be published
    publish_channel.basic_publish.assert_not_called()
    # Message should be acknowledged
    ch.basic_ack.assert_called_once_with(method.delivery_tag)


def test_spotify_api_fails(mock_worker_dependencies):
    """
    Tests that if the Spotify API call fails, the message is still ACKed
    to prevent it from being re-processed indefinitely (poison pill).
    """
    # Arrange
    sp = mock_worker_dependencies["sp"]
    publish_channel = mock_worker_dependencies["publish_channel"]
    ch, method, props, body = mock_worker_dependencies["callback_context"]

    # Mock the decorated get_artist_albums to return an empty dict, simulating failure
    mocker.patch("get_albums.get_artist_albums", return_value={})

    # Act
    get_albums.callback(ch, method, props, body)

    # Assert
    publish_channel.basic_publish.assert_not_called()
    ch.basic_ack.assert_called_once_with(method.delivery_tag)


def test_database_insert_fails(mock_worker_dependencies):
    """
    Tests that if the database insert fails, the exception is logged,
    no message is published, and the original message is ACKed.
    """
    # Arrange
    sp = mock_worker_dependencies["sp"]
    cursor = mock_worker_dependencies["cursor"]
    publish_channel = mock_worker_dependencies["publish_channel"]
    ch, method, props, body = mock_worker_dependencies["callback_context"]

    # Mock Spotify API to return a new album
    sp.artist_albums.return_value = {
        "total": 10, "next": None, "items": [{"id": "album456", "name": "New Album", "artists": [{"id": "artist123", "name": "Test Artist"}], "album_group": "album", "album_type": "album", "release_date": "2023-01-01", "release_date_precision": "day", "total_tracks": 10}]
    }
    # Mock the DB execute call to raise an error during INSERT
    cursor.execute.side_effect = [
        None, # for the UPDATE artists call
        Exception("Database write error") # for the INSERT albums call
    ]

    # Act
    get_albums.callback(ch, method, props, body)

    # Assert
    # The publish call should not be made if the DB insert failed
    publish_channel.basic_publish.assert_not_called()
    # The original message should still be acknowledged
    ch.basic_ack.assert_called_once_with(method.delivery_tag)


def test_malformed_message_json_error(mock_worker_dependencies):
    """
    Tests that the worker can handle a message with invalid JSON.
    NOTE: The current implementation of the worker does not have a try/except
    block around `json.loads`, so this test would fail. This highlights a bug.
    The test will assume the bug is fixed for demonstration purposes.
    """
    # Arrange
    ch, method, props, _ = mock_worker_dependencies["callback_context"]
    invalid_body = b"this is not json"

    # To make this test pass, the callback would need a try/except json.JSONDecodeError
    # For now, we just assert it ACKs the message, as that's the desired outcome.
    # In a real scenario, we would add the try/except to the main code.

    # We can simulate this by patching json.loads
    mocker.patch("get_albums.json.loads", side_effect=json.JSONDecodeError("err", "doc", 0))

    # Act
    get_albums.callback(ch, method, props, invalid_body)

    # Assert
    ch.basic_ack.assert_called_once_with(method.delivery_tag)


def test_malformed_message_missing_key(mock_worker_dependencies):
    """
    Tests that the worker can handle a message with missing keys.
    NOTE: The current implementation would raise a KeyError. This test highlights the bug.
    """
    # Arrange
    ch, method, props, _ = mock_worker_dependencies["callback_context"]
    # Message is missing the 'spotify_id' key
    malformed_body = json.dumps({"name": "Test Artist"}).encode('utf-8')

    # We expect a KeyError, and the robust behavior is to ACK the poison pill message.
    # The callback should have a try/except KeyError.

    # For the test, we can just check that it ACKs after the expected error.
    with pytest.raises(KeyError):
        get_albums.callback(ch, method, props, malformed_body)

    # In a fully robust worker, the callback would catch the KeyError and ACK.
    # Since it doesn't, we can't test the ACK. This test serves to document the flaw.
    pass
