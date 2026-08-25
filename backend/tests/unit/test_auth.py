"""
Unit tests for authentication and security functions.
"""
import pytest
from uuid import uuid4
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    decode_token,
)

def test_password_hashing():
    pwd = "SuperSecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_access_token():
    user_id = str(uuid4())
    token = create_access_token(user_id)
    assert token is not None
    
    decoded_user_id = verify_access_token(token)
    assert decoded_user_id == user_id
    
    # Check payload structure
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "exp" in payload

def test_jwt_refresh_token():
    user_id = str(uuid4())
    token = create_refresh_token(user_id)
    assert token is not None
    
    decoded_user_id = verify_refresh_token(token)
    assert decoded_user_id == user_id
    
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    
    # Access token verifier should reject a refresh token
    assert verify_access_token(token) is None
