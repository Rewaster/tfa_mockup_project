from pydantic import BaseModel


class JwtTokenSchema(BaseModel):
    """JWT token information storage class"""

    access_token: str
    refresh_token: str


class JwtTokenPayload(BaseModel):
    """JWT token payload information storage class"""

    sub: int = None
    exp: int = None


class PreTfaJwtTokenSchema(JwtTokenSchema):
    """JWT pre-TFA token information storage class"""

    refresh_token: None
