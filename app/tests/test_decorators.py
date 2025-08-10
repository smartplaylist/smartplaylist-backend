import pytest
from unittest.mock import Mock, call
from spotipy.exceptions import SpotifyException
from imports.decorators import api_attempts

# A dummy logger for the decorator to use
@pytest.fixture(autouse=True)
def mock_logger(mocker):
    mocker.patch("imports.decorators.get_logger", return_value=Mock())

def test_api_attempts_success_first_try():
    """
    Tests that the decorator returns the function's result on the first try if it succeeds.
    """
    mock_func = Mock(return_value={"success": True})

    # Decorate the function
    decorated_func = api_attempts(mock_func)

    # Call the decorated function
    result = decorated_func("some_arg")

    # Assertions
    assert result == {"success": True}
    mock_func.assert_called_once_with("some_arg")

def test_api_attempts_succeeds_after_failure():
    """
    Tests that the decorator successfully returns a result after one failure.
    """
    mock_func = Mock(side_effect=[
        SpotifyException(429, -1, "Too Many Requests"),
        {"success": True}
    ])

    decorated_func = api_attempts(mock_func)
    result = decorated_func("some_arg")

    assert result == {"success": True}
    assert mock_func.call_count == 2
    mock_func.assert_has_calls([call("some_arg"), call("some_arg")])

def test_api_attempts_fails_after_all_retries():
    """
    Tests that the decorator returns an empty dict after all retry attempts fail.
    """
    mock_func = Mock(side_effect=SpotifyException(429, -1, "Too Many Requests"))

    # Use a smaller number of retries for the test
    decorated_func = api_attempts(_func=mock_func, num_times=3)
    result = decorated_func("some_arg")

    # Assert that it returns the default empty dict
    assert result == {}
    # Assert it was called 3 times
    assert mock_func.call_count == 3

def test_api_attempts_handles_generic_exception():
    """
    Tests that the decorator can handle generic exceptions, not just SpotifyException.
    """
    mock_func = Mock(side_effect=Exception("A generic error"))

    decorated_func = api_attempts(_func=mock_func, num_times=3)
    result = decorated_func("some_arg")

    assert result == {}
    assert mock_func.call_count == 3
