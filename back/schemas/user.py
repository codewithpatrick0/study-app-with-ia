from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

class UserCreate(BaseModel):
    """Data the client sends to register."""
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=8, max_length=128)  # Hidden in logs and reprs

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, email: str) -> str:
        """Store emails in one form so 'Ana@Mail.com' and 'ana@mail.com' count as the same."""
        return email.lower()

class UserRead(BaseModel):
    """Data the API returns about a user; never includes the password hash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
