import pytest
from unittest.mock import patch, MagicMock
from backend.app.core.config import Settings

# We need to ensure 'backend.app.core.rate_limiter.settings' is patched,
# and also 'redis.Redis' if we are testing its call.

@pytest.fixture
def mock_settings_no_redis():
    return Settings(REDIS_HOST=None, RATE_LIMIT_ENABLED=True)

@pytest.fixture
def mock_settings_with_redis_success():
    return Settings(REDIS_HOST="testhost", REDIS_PORT=1234, RATE_LIMIT_ENABLED=True)

@pytest.fixture
def mock_settings_with_redis_failure():
    return Settings(REDIS_HOST="testhost", REDIS_PORT=1234, RATE_LIMIT_ENABLED=True)

@patch('backend.app.core.rate_limiter.settings') # Patch where 'settings' is used
def test_get_storage_uri_no_redis_configured(mock_settings_obj, mock_settings_no_redis):
    mock_settings_obj.RATE_LIMIT_ENABLED = mock_settings_no_redis.RATE_LIMIT_ENABLED
    mock_settings_obj.REDIS_HOST = mock_settings_no_redis.REDIS_HOST

    from backend.app.core.rate_limiter import get_storage_uri # Import late
    uri = get_storage_uri()
    assert uri == "memory://"

@patch('redis.Redis') # Patch 'redis.Redis' where it's imported and used
@patch('backend.app.core.rate_limiter.settings')
def test_get_storage_uri_redis_configured_and_success(mock_settings_obj, mock_redis_constructor, mock_settings_with_redis_success):
    mock_settings_obj.RATE_LIMIT_ENABLED = mock_settings_with_redis_success.RATE_LIMIT_ENABLED
    mock_settings_obj.REDIS_HOST = mock_settings_with_redis_success.REDIS_HOST
    mock_settings_obj.REDIS_PORT = mock_settings_with_redis_success.REDIS_PORT

    mock_redis_instance = MagicMock()
    mock_redis_constructor.return_value = mock_redis_instance
    mock_redis_instance.ping.return_value = True # Simulate successful ping

    from backend.app.core.rate_limiter import get_storage_uri # Import late
    uri = get_storage_uri()
    assert uri == f"redis://{mock_settings_with_redis_success.REDIS_HOST}:{mock_settings_with_redis_success.REDIS_PORT}"
    mock_redis_constructor.assert_called_once_with(
        host=mock_settings_with_redis_success.REDIS_HOST,
        port=mock_settings_with_redis_success.REDIS_PORT,
        socket_connect_timeout=1,
        socket_timeout=1
    )
    mock_redis_instance.ping.assert_called_once()

@patch('redis.Redis') # Patch 'redis.Redis'
@patch('backend.app.core.rate_limiter.settings')
def test_get_storage_uri_redis_configured_but_ping_fails(mock_settings_obj, mock_redis_constructor, mock_settings_with_redis_failure):
    mock_settings_obj.RATE_LIMIT_ENABLED = mock_settings_with_redis_failure.RATE_LIMIT_ENABLED
    mock_settings_obj.REDIS_HOST = mock_settings_with_redis_failure.REDIS_HOST
    mock_settings_obj.REDIS_PORT = mock_settings_with_redis_failure.REDIS_PORT

    mock_redis_instance = MagicMock()
    mock_redis_constructor.return_value = mock_redis_instance

    # Import redis exceptions for side_effect
    import redis
    mock_redis_instance.ping.side_effect = redis.exceptions.ConnectionError("Ping failed")

    from backend.app.core.rate_limiter import get_storage_uri # Import late
    uri = get_storage_uri()
    assert uri == "memory://"
    mock_redis_constructor.assert_called_once_with(
        host=mock_settings_with_redis_failure.REDIS_HOST,
        port=mock_settings_with_redis_failure.REDIS_PORT,
        socket_connect_timeout=1,
        socket_timeout=1
    )
    mock_redis_instance.ping.assert_called_once()


@patch('backend.app.core.rate_limiter.settings')
def test_get_storage_uri_rate_limit_disabled(mock_settings_obj, mock_settings_no_redis):
    # Even if redis is configured, if RATE_LIMIT_ENABLED is false, it should use memory (or follow logic)
    # Current get_storage_uri logic: if RATE_LIMIT_ENABLED is false, it still tries Redis if configured.
    # Let's test that behavior. If RATE_LIMIT_ENABLED is false, the limiter itself uses a high passthrough limit.
    # The storage URI selection is independent of RATE_LIMIT_ENABLED in the current code.

    mock_settings_obj.RATE_LIMIT_ENABLED = False # Explicitly disable
    mock_settings_obj.REDIS_HOST = mock_settings_no_redis.REDIS_HOST # No redis host

    from backend.app.core.rate_limiter import get_storage_uri # Import late
    uri = get_storage_uri()
    assert uri == "memory://"


@patch('redis.Redis')
@patch('backend.app.core.rate_limiter.settings')
def test_get_storage_uri_rate_limit_disabled_with_redis(mock_settings_obj, mock_redis_constructor, mock_settings_with_redis_success):
    mock_settings_obj.RATE_LIMIT_ENABLED = False # Explicitly disable
    mock_settings_obj.REDIS_HOST = mock_settings_with_redis_success.REDIS_HOST
    mock_settings_obj.REDIS_PORT = mock_settings_with_redis_success.REDIS_PORT

    mock_redis_instance = MagicMock()
    mock_redis_constructor.return_value = mock_redis_instance
    mock_redis_instance.ping.return_value = True

    from backend.app.core.rate_limiter import get_storage_uri # Import late
    uri = get_storage_uri()
    # get_storage_uri prioritizes Redis if configured and working, regardless of RATE_LIMIT_ENABLED
    assert uri == f"redis://{mock_settings_with_redis_success.REDIS_HOST}:{mock_settings_with_redis_success.REDIS_PORT}"
