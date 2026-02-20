from pydantic import BaseModel, EmailStr

class StudentRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    usn: str
    semester_id: int