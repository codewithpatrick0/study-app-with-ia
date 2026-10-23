from pydantic import BaseModel, ConfigDict, Field, SecretStr

class LoginRequest(BaseModel):
    """Credentials the client sends to log in."""
    model_config = ConfigDict(str_strip_whitespace=True)

    username_or_email: str = Field(min_length=1, max_length=255)
    password: SecretStr = Field(min_length=1, max_length=128)

class Token(BaseModel):
    """What the API returns after a successful login."""
    access_token: str
    token_type: str = "bearer"
