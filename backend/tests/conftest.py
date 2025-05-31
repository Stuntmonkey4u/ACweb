# Pytest conftest.py for shared fixtures
# Example:
# import pytest
# from backend.app.core.config import settings

# @pytest.fixture(scope="session", autouse=True)
# def override_settings_for_testing():
#     # Override settings for testing if necessary
#     # For example, to use a test database or disable external calls
#     # settings.SOME_SETTING = "test_value"
#     pass
