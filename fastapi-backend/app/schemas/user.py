from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False
    credits: int = 0
    is_active: bool = True
    

class UserLogin(BaseModel):
    username: str
    password: str
    is_admin: bool = False
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    credits: int
    is_admin: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str