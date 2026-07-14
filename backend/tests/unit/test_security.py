"""
Unit tests for security utilities.
Tests password hashing, JWT creation/decoding, and token validation.
"""

import pytest
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    validate_password_policy,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_returns_string(self):
        result = hash_password("SecurePass123!")
        assert isinstance(result, str)
        assert result.startswith("$2b$")

    def test_hash_password_different_each_time(self):
        h1 = hash_password("SecurePass123!")
        h2 = hash_password("SecurePass123!")
        assert h1 != h2

    def test_verify_password_correct(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("SecurePass123!", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("WrongPass123!", hashed) is False

    def test_verify_password_empty(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("", hashed) is False

    def test_hash_password_special_chars(self):
        hashed = hash_password("P@ssw0rd!#$%")
        assert verify_password("P@ssw0rd!#$%", hashed) is True


class TestJWT:
    """Test JWT token creation and decoding."""

    def test_create_access_token_returns_string(self):
        token = create_access_token(data={"sub": "user@test.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        token = create_access_token(data={"sub": "user@test.com", "role": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "user@test.com"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_decode_token_wrong_secret(self):
        from fastapi import HTTPException
        from app.config import settings
        original = settings.SECRET_KEY
        token = create_access_token(data={"sub": "user@test.com"})
        settings.SECRET_KEY = "wrong-secret-key-for-testing-32chars-long!!"
        try:
            with pytest.raises(HTTPException) as exc_info:
                decode_token(token)
            assert exc_info.value.status_code == 401
        finally:
            settings.SECRET_KEY = original

    def test_token_expiry(self):
        from fastapi import HTTPException
        token = create_access_token(
            data={"sub": "user@test.com"},
            expires_delta=timedelta(seconds=1)
        )
        import time
        time.sleep(2)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401


class TestPasswordPolicy:
    """Test password policy validation."""

    def test_valid_password(self):
        valid, msg = validate_password_policy("SecurePass123!")
        assert valid is True

    def test_too_short(self):
        valid, msg = validate_password_policy("Abc1!")
        assert valid is False
        assert "12" in msg or "characters" in msg.lower() or "minimum" in msg.lower()

    def test_no_uppercase(self):
        valid, msg = validate_password_policy("securepass123!")
        assert valid is False

    def test_no_lowercase(self):
        valid, msg = validate_password_policy("SECUREPASS123!")
        assert valid is False

    def test_no_number(self):
        valid, msg = validate_password_policy("SecurePass!")
        assert valid is False

    def test_no_symbol(self):
        valid, msg = validate_password_policy("SecurePass123")
        assert valid is False

    def test_empty_password(self):
        valid, msg = validate_password_policy("")
        assert valid is False
