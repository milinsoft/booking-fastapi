from pydantic import BaseModel, EmailStr


class SUserPublic(BaseModel):
    email: EmailStr


class SUserAuth(SUserPublic):
    password: str
