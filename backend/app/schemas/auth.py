from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_id: str
    captcha_code: str


class CaptchaResponse(BaseModel):
    captcha_id: str
    image: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: str
    username: str
    role: str
    employee_id: str | None = None
    employee_name: str | None = None


class UserInfo(BaseModel):
    id: str
    username: str
    role: str
    employee_id: str | None = None
    employee_name: str | None = None

    class Config:
        from_attributes = True
