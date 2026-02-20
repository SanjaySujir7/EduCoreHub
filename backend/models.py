from sqlalchemy import Column, Integer, String, Enum, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    ADMIN = 'ADMIN'
    FACULTY = 'FACULTY'
    STUDENT = 'STUDENT'

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)

class Semester(Base):
    __tablename__ = "semesters"
    
    semester_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    semester_number = Column(Integer, unique=True)

class Student(Base):
    __tablename__ = "students"
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    usn = Column(String(20), unique=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id", ondelete="CASCADE"))

    # Relationships
    user = relationship("User", back_populates="student_profile")