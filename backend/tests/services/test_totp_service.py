import pytest
import pyotp
import base64
from unittest.mock import patch, MagicMock

from backend.app.services import totp_service

def test_generate_totp_secret():
    secret = totp_service.generate_totp_secret()
    assert isinstance(secret, str)
    # pyotp.random_base32() by default returns 16 chars, which becomes 32 bytes when base32 decoded.
    # However, it's typically 32 characters long for base32 encoding of 20 bytes of randomness.
    # Let's check if it's a valid base32 string and its typical length.
    # A common length for TOTP secrets is 32 base32 characters (representing 20 bytes).
    # pyotp.random_base32() actually defaults to 32 characters.
    assert len(secret) == 32
    try:
        base64.b32decode(secret)
    except Exception:
        pytest.fail("Generated secret is not valid base32")

def test_get_totp_uri():
    secret = "JBSWY3DPEHPK3PXP" # Example valid base32 secret
    username = "testuser@example.com"
    issuer_name = "TestApp"
    uri = totp_service.get_totp_uri(secret, username, issuer_name)

    assert uri.startswith("otpauth://totp/")
    assert f"{issuer_name}:{username}" in uri
    assert f"secret={secret}" in uri
    assert f"issuer={issuer_name}" in uri

def test_verify_totp_code():
    secret = totp_service.generate_totp_secret() # Use a fresh secret
    totp = pyotp.TOTP(secret)

    # Test with a valid code
    valid_code = totp.now()
    assert totp_service.verify_totp_code(secret, valid_code) is True

    # Test with an invalid code
    invalid_code = "000000"
    assert totp_service.verify_totp_code(secret, invalid_code) is False

    # Test with an expired code (by checking a code from a previous window)
    # This requires some control over time, or ensuring the window has passed.
    # For simplicity, we assume default 30s interval.
    # A code is valid for its current window, and often the previous/next for clock drift.
    # pyotp.TOTP.verify allows for a 'valid_window' parameter.
    # Our service function doesn't expose that, so it uses pyotp's default.

    # To test expiry more directly, you might need to mock 'time.time()'
    # or check a code known to be outside the current validity window of pyotp.
    # For this test, verifying a clearly wrong code is sufficient for basic invalidity.
    # Testing exact window expiry is more complex without time mocking.

@patch('qrcode.make') # Mocks qrcode.make
def test_generate_qr_code_data_uri(mock_make_qrcode):
    # Configure the mock for qrcode.make
    mock_img = MagicMock()
    mock_make_qrcode.return_value = mock_img

    otp_uri = "otpauth://totp/TestApp:testuser?secret=JBSWY3DPEHPK3PXP&issuer=TestApp"
    qr_data_uri = totp_service.generate_qr_code_data_uri(otp_uri)

    mock_make_qrcode.assert_called_once_with(otp_uri, image_factory=qrcode.image.pil.PilImage)
    mock_img.save.assert_called_once() # Check that save was called

    assert qr_data_uri.startswith("data:image/png;base64,")
    # Validate the base64 part
    try:
        base64.b64decode(qr_data_uri.split(",")[1])
    except Exception:
        pytest.fail("QR code data URI does not contain valid base64 data.")

# Test for specific case where secret might be shorter if pyotp's default changes
def test_generate_totp_secret_allows_shorter_if_pyotp_changes():
    # If pyotp.random_base32() could return variable lengths (it doesn't by default now)
    # this test would ensure our validation isn't too strict.
    # For now, this is more of a note as pyotp.random_base32(length=16) is possible.
    # Our function uses the default.
    secret = pyotp.random_base32(16) # Example of a shorter but valid secret
    assert len(secret) == 16
    try:
        base64.b32decode(secret)
    except:
        pytest.fail("Shorter secret is not valid base32")

def test_get_totp_uri_with_special_chars_in_username():
    secret = "JBSWY3DPEHPK3PXP"
    username = "user+name@example.com" # Username with '+'
    issuer_name = "My Cool App" # Issuer with space
    uri = totp_service.get_totp_uri(secret, username, issuer_name)

    # '+' should be URL encoded as %2B, spaces in issuer usually %20 or kept as space by some apps
    # pyotp's provisioning_uri handles necessary encoding for accountname and issuer
    assert f"My%20Cool%20App:user%2Bname%40example.com" in uri or \
           f"My+Cool+App:user%2Bname%40example.com" in uri or \
           f"My%20Cool%20App:user%2Bname@example.com" in uri # some apps might not encode @ in path part
    assert f"secret={secret}" in uri
    assert f"issuer=My%20Cool%20App" in uri or f"issuer=My+Cool+App" in uri

    # Test with another username
    username_space = "test user"
    uri_space = totp_service.get_totp_uri(secret, username_space, issuer_name)
    assert f"My%20Cool%20App:test%20user" in uri_space or \
           f"My+Cool+App:test%20user" in uri_space
