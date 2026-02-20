from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import Base, User, Student, RoleEnum
from schemas import StudentRegister
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/educorehub"

engine = create_engine(SQLALCHEMY_DATABASE_URL) # Removed the SQLite-specific connect_args
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Departmental Digital Resource & Knowledge Hub")

# --- Password Hashing Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Registration Endpoint ---
@app.post("/register/student", status_code=status.HTTP_201_CREATED)
def register_student(student_data: StudentRegister, db: Session = Depends(get_db)):
    
        
    # 2. Check if USN already exists to prevent duplicates 
    existing_student_usn = db.query(Student).filter(Student.usn == student_data.usn).first()
    if existing_student_usn:
        raise HTTPException(status_code=400, detail="USN already registered")
    
    # 1. Check if email already exists
    existing_user_email = db.query(User).filter(User.email == student_data.email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 3. Create User record
    hashed_pwd = get_password_hash(student_data.password)
    new_user = User(
        full_name=student_data.full_name, # Students must sign up using their Name 
        email=student_data.email,
        password_hash=hashed_pwd,
        role=RoleEnum.STUDENT
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Get the generated user_id

    # 4. Create Student specific record
    new_student = Student(
        user_id=new_user.user_id,
        usn=student_data.usn, # Students must sign up using their USN 
        semester_id=student_data.semester_id # Students must sign up using their Semester 
    )
    
    db.add(new_student)
    db.commit()
    
    return {"message": "Student registered successfully", "user_id": new_user.user_id}