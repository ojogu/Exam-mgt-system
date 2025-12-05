from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email:EmailStr
    password:str
    

class Register(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    school_id: str
