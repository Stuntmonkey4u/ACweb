import pytest
from unittest.mock import patch, MagicMock
from backend.app.services import email_service
from backend.app.core.config import Settings # To override settings

# Sample settings override for testing
@pytest.fixture
def mock_settings_configured():
    original_settings = email_service.settings
    test_settings = Settings(
        SMTP_HOST="smtp.test.com",
        SMTP_PORT=587,
        SMTP_USER="testuser",
        SMTP_PASSWORD="testpassword",
        SMTP_SENDER_EMAIL="sender@test.com",
        FRONTEND_URL="http://localhost:3000",
        APP_NAME="TestApp" # Add other required fields if Settings class evolves
    )
    email_service.settings = test_settings
    yield test_settings
    email_service.settings = original_settings # Restore original

@pytest.fixture
def mock_settings_unconfigured():
    original_settings = email_service.settings
    test_settings = Settings(
        SMTP_HOST=None, # Unconfigured
        FRONTEND_URL="http://localhost:3000",
        APP_NAME="TestApp"
    )
    email_service.settings = test_settings
    yield test_settings
    email_service.settings = original_settings

@patch('socket.socket')
def test_is_online_success(mock_socket_constructor):
    mock_socket_instance = MagicMock()
    mock_socket_constructor.return_value = mock_socket_instance
    mock_socket_instance.connect.return_value = None # Simulate successful connection

    assert email_service.is_online() is True
    mock_socket_instance.connect.assert_called_once_with(("8.8.8.8", 53))

@patch('socket.socket')
def test_is_online_failure(mock_socket_constructor):
    mock_socket_instance = MagicMock()
    mock_socket_constructor.return_value = mock_socket_instance
    mock_socket_instance.connect.side_effect = socket.error("Connection failed")

    assert email_service.is_online() is False

# Need to import socket for the side_effect above
import socket

@patch('smtplib.SMTP')
@patch('backend.app.services.email_service.is_online', return_value=True)
def test_send_verification_email_success(mock_is_online, mock_smtp_constructor, mock_settings_configured):
    mock_smtp_instance = MagicMock()
    mock_smtp_constructor.return_value.__enter__.return_value = mock_smtp_instance # For 'with' statement

    user_email = "recipient@example.com"
    username = "test_user"
    verification_token = "test_token_123"

    result = email_service.send_verification_email(user_email, username, verification_token)

    assert result is True
    mock_smtp_constructor.assert_called_once_with(mock_settings_configured.SMTP_HOST, mock_settings_configured.SMTP_PORT)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with(mock_settings_configured.SMTP_USER, mock_settings_configured.SMTP_PASSWORD)

    # Check sendmail arguments
    args, _ = mock_smtp_instance.sendmail.call_args
    assert args[0] == mock_settings_configured.SMTP_SENDER_EMAIL
    assert args[1] == [user_email]

    # Check email content (simplified check)
    email_body = args[2]
    assert f"Hi {username}" in email_body
    assert f"{mock_settings_configured.FRONTEND_URL}/verify-email?token={verification_token}" in email_body
    assert "Subject: Verify your email address" in email_body # Check subject header

@patch('smtplib.SMTP')
@patch('backend.app.services.email_service.is_online', return_value=True)
def test_send_verification_email_smtp_auth_error(mock_is_online, mock_smtp_constructor, mock_settings_configured):
    mock_smtp_instance = MagicMock()
    mock_smtp_constructor.return_value.__enter__.return_value = mock_smtp_instance
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication credentials invalid")

    result = email_service.send_verification_email("r@ex.com", "u", "t")
    assert result is False

@patch('smtplib.SMTP')
@patch('backend.app.services.email_service.is_online', return_value=False) # Offline
def test_send_verification_email_offline(mock_is_online, mock_smtp_constructor, mock_settings_configured):
    result = email_service.send_verification_email("r@ex.com", "u", "t")
    assert result is False
    mock_smtp_constructor.assert_not_called() # SMTP should not be initiated if offline

@patch('smtplib.SMTP')
@patch('backend.app.services.email_service.is_online', return_value=True)
def test_send_verification_email_smtp_not_configured(mock_is_online, mock_smtp_constructor, mock_settings_unconfigured):
    # Using mock_settings_unconfigured where SMTP_HOST is None
    result = email_service.send_verification_email("r@ex.com", "u", "t")
    assert result is False
    mock_smtp_constructor.assert_not_called()

# Need to import smtplib for SMTPAuthenticationError
import smtplib
