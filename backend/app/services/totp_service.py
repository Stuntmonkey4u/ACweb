import pyotp
import qrcode
import qrcode.image.pil
import io
import base64

def generate_totp_secret() -> str:
    """Generates a new base32 TOTP secret."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, username: str, issuer_name: str = "AzerothCoreManager") -> str:
    """
    Generates an otpauth:// URI for use with authenticator apps.
    Includes username (email for uniqueness if needed) and issuer name.
    """
    # Ensure username is suitable for URI, typically an email address or account name.
    # For AzerothCore, username should be unique.
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

def verify_totp_code(secret: str, code: str) -> bool:
    """Verifies a TOTP code against the secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def generate_qr_code_data_uri(otp_uri: str) -> str:
    """Generates a QR code for the OTP URI and returns it as a base64 encoded PNG data URI."""
    img = qrcode.make(otp_uri, image_factory=qrcode.image.pil.PilImage)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
