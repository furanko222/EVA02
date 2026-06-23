from typing import Optional

from pydantic import BaseModel, Field, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Unique email of the user")
    is_active: Optional[bool] = Field(True, description="")
    is_superuser: Optional[bool] = Field(False, description="Gives user control over other users")
    full_name: Optional[str] = Field(None, title="Full Name", examples=["John Doe"])


class UserBaseInDB(UserBase):
    id: int = None


# Properties to receive via API on creation
class UserInCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserInUpdate(UserBase):
    password: Optional[str] = None


# Additional properties to return via API
class User(UserBaseInDB):
    pass


# Additional properties stored in DB
class UserInDB(UserBaseInDB):
    hashed_password: str
