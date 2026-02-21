import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException, status, Request, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import bcrypt
import jwt
import os
import shutil
import uuid
import random
import smtplib
import csv
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()
SMTP_EMAIL    = os.getenv("Email", "")
SMTP_APP_PASS = os.getenv("app_password", "")

# ── In-memory OTP store  {email: {otp, expires_at}} ──────────────────────────
password_reset_otps: dict = {}

app = FastAPI(title="EduCoreHub API")

# ── JWT Config ───────────────────────────────────────────────────────────────
SECRET_KEY = "educorehub-super-secret-key-2024"   # Change in production!
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Templates & Uploads ──────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/login")

@app.get("/register", response_class=HTMLResponse)
async def serve_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def serve_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/faculty/login", response_class=HTMLResponse)
async def serve_faculty_login(request: Request):
    return templates.TemplateResponse("faculty_login.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def serve_admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_student_dashboard(request: Request):
    return templates.TemplateResponse("student_dashboard.html", {"request": request})

@app.get("/faculty/dashboard", response_class=HTMLResponse)
async def serve_faculty_dashboard(request: Request):
    return templates.TemplateResponse("faculty_dashboard.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def serve_admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse)
async def serve_forgot_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',        # XAMPP default
            database='educorehub'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def hash_password(password: str) -> str:
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(request: Request) -> dict:
    """Extract and validate JWT from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    token = auth.split(" ", 1)[1]
    return decode_token(token)


# ══════════════════════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class StudentRegisterRequest(BaseModel):
    full_name: str
    email: str
    usn: str
    semester_number: int
    password: str
    phone: Optional[str] = None

class StudentRegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRATION
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/register", response_model=StudentRegisterResponse)
def register_student(student: StudentRegisterRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (student.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Email is already registered.")

        cursor.execute("SELECT user_id FROM students WHERE usn = %s", (student.usn,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="USN is already registered.")

        cursor.execute("SELECT semester_id FROM semesters WHERE semester_number = %s", (student.semester_number,))
        sem_row = cursor.fetchone()
        if not sem_row:
            cursor.execute("INSERT INTO semesters (semester_number) VALUES (%s)", (student.semester_number,))
            semester_id = cursor.lastrowid
        else:
            semester_id = sem_row['semester_id']

        hashed_pw = hash_password(student.password)
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'STUDENT')",
            (student.full_name, student.email, hashed_pw)
        )
        user_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO students (user_id, usn, semester_id) VALUES (%s, %s, %s)",
            (user_id, student.usn, semester_id)
        )
        conn.commit()
        return {"message": "Student registered successfully."}

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

def _do_login(email: str, password: str, expected_role: str) -> LoginResponse:
    """Shared login logic for all roles."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id, full_name, email, password_hash, role FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if user['role'] != expected_role:
            raise HTTPException(
                status_code=403,
                detail=f"This login is for {expected_role.title()} accounts only."
            )

        if not verify_password(password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        token = create_access_token({
            "sub": str(user['user_id']),
            "role": user['role'],
            "name": user['full_name'],
        })

        return LoginResponse(
            access_token=token,
            role=user['role'],
            full_name=user['full_name'],
            user_id=user['user_id'],
        )
    finally:
        cursor.close()
        conn.close()


@app.post("/api/login", response_model=LoginResponse)
def student_login(body: LoginRequest):
    """Student login endpoint."""
    return _do_login(body.email, body.password, "STUDENT")


@app.post("/api/faculty/login", response_model=LoginResponse)
def faculty_login(body: LoginRequest):
    """Faculty login endpoint."""
    return _do_login(body.email, body.password, "FACULTY")


@app.post("/api/admin/login", response_model=LoginResponse)
def admin_login(body: LoginRequest):
    """Admin / HOD login endpoint."""
    return _do_login(body.email, body.password, "ADMIN")


# ══════════════════════════════════════════════════════════════════════════════
#  STUDENT DASHBOARD API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /api/student/profile ─────────────────────────────────────────────────
@app.get("/api/student/profile")
def get_student_profile(request: Request):
    """Return the logged-in student's full profile."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.email, u.role, u.created_at,
                   s.usn, sem.semester_number
            FROM users u
            LEFT JOIN students s ON u.user_id = s.user_id
            LEFT JOIN semesters sem ON s.semester_id = sem.semester_id
            WHERE u.user_id = %s
        """, (user_id,))
        profile = cursor.fetchone()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert datetime to string for JSON
        if profile.get('created_at'):
            profile['created_at'] = profile['created_at'].isoformat()

        return profile
    finally:
        cursor.close()
        conn.close()


# ── GET /api/student/dashboard-stats ─────────────────────────────────────────
@app.get("/api/student/dashboard-stats")
def get_dashboard_stats(request: Request):
    """Return stat card counts for the student dashboard."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        # My uploads count
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE uploaded_by = %s", (user_id,))
        my_uploads = cursor.fetchone()['cnt']

        # Available (approved) resources
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE status = 'APPROVED'")
        available = cursor.fetchone()['cnt']

        # My pending uploads
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE uploaded_by = %s AND status = 'PENDING'", (user_id,))
        pending = cursor.fetchone()['cnt']

        # Active notices
        cursor.execute("SELECT COUNT(*) as cnt FROM notices")
        notices = cursor.fetchone()['cnt']

        return {
            "my_uploads": my_uploads,
            "available_resources": available,
            "pending_uploads": pending,
            "active_notices": notices
        }
    finally:
        cursor.close()
        conn.close()


# ── GET /api/resources ───────────────────────────────────────────────────────
@app.get("/api/resources")
def get_resources(
    q: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None, alias="type"),
    limit: Optional[int] = Query(None),
):
    """Return approved resources with optional filters."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT r.resource_id, r.title, r.description, r.file_path, r.file_type,
                   r.status, r.created_at,
                   u.full_name AS uploaded_by_name,
                   sub.subject_code, sub.subject_name,
                   sem.semester_number
            FROM resources r
            JOIN users u ON r.uploaded_by = u.user_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            JOIN semesters sem ON sub.semester_id = sem.semester_id
            WHERE r.status = 'APPROVED'
        """
        params = []

        if q:
            query += " AND (r.title LIKE %s OR sub.subject_code LIKE %s OR sub.subject_name LIKE %s)"
            like = f"%{q}%"
            params.extend([like, like, like])

        if semester:
            query += " AND sem.semester_number = %s"
            params.append(semester)

        if subject:
            query += " AND sub.subject_code = %s"
            params.append(subject)

        if file_type:
            query += " AND r.file_type = %s"
            params.append(file_type)

        query += " ORDER BY r.created_at DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cursor.execute(query, tuple(params))
        resources = cursor.fetchall()

        # Convert datetimes
        for r in resources:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].isoformat()

        return resources
    finally:
        cursor.close()
        conn.close()


# ── GET /api/student/my-uploads ──────────────────────────────────────────────
@app.get("/api/student/my-uploads")
def get_my_uploads(request: Request):
    """Return all resources uploaded by the current student."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.resource_id, r.title, r.description, r.file_path, r.file_type,
                   r.status, r.created_at,
                   sub.subject_code, sub.subject_name
            FROM resources r
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE r.uploaded_by = %s
            ORDER BY r.created_at DESC
        """, (user_id,))
        uploads = cursor.fetchall()

        for u in uploads:
            if u.get('created_at'):
                u['created_at'] = u['created_at'].isoformat()

        return uploads
    finally:
        cursor.close()
        conn.close()


# ── POST /api/student/upload ─────────────────────────────────────────────────
@app.post("/api/student/upload")
async def upload_resource(
    request: Request,
    title: str = Form(...),
    subject_id: int = Form(...),
    file_type: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):
    """Upload a new resource file. Requires JWT auth."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    # Validate file extension
    allowed_exts = {'.pdf', '.ppt', '.pptx', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Save file with unique name
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    conn = get_db_connection()
    if not conn:
        os.remove(file_path)  # cleanup
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO resources (title, description, file_path, file_type, uploaded_by, subject_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')
        """, (title, description, unique_name, file_type, user_id, subject_id))
        conn.commit()
        return {"message": "Resource uploaded successfully. It will be reviewed before publishing.", "resource_id": cursor.lastrowid}
    except Error as e:
        conn.rollback()
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── GET /api/notices ─────────────────────────────────────────────────────────
@app.get("/api/notices")
def get_notices(limit: Optional[int] = Query(None)):
    """Return all notices ordered by newest first."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT n.notice_id, n.title, n.content, n.created_at,
                   u.full_name AS posted_by, n.posted_by AS posted_by_id
            FROM notices n
            JOIN users u ON n.posted_by = u.user_id
            ORDER BY n.created_at DESC
        """
        params = []
        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cursor.execute(query, tuple(params))
        notices = cursor.fetchall()

        for n in notices:
            if n.get('created_at'):
                n['created_at'] = n['created_at'].isoformat()

        return notices
    finally:
        cursor.close()
        conn.close()


# ── GET /api/subjects ────────────────────────────────────────────────────────
@app.get("/api/subjects")
def get_subjects():
    """Return all subjects with their semester info."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sub.subject_id, sub.subject_code, sub.subject_name,
                   sem.semester_number
            FROM subjects sub
            JOIN semesters sem ON sub.semester_id = sem.semester_id
            ORDER BY sem.semester_number, sub.subject_code
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ── GET /api/resources/{id}/download ─────────────────────────────────────────
@app.get("/api/resources/{resource_id}/download")
def download_resource(resource_id: int):
    """Serve a resource file for download."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT title, file_path, file_type FROM resources WHERE resource_id = %s", (resource_id,))
        resource = cursor.fetchone()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        file_full_path = os.path.join(UPLOAD_DIR, resource['file_path'])
        if not os.path.exists(file_full_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        return FileResponse(
            path=file_full_path,
            filename=resource['title'] + os.path.splitext(resource['file_path'])[1],
            media_type='application/octet-stream'
        )
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  FACULTY DASHBOARD API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /api/faculty/profile ─────────────────────────────────────────────────
@app.get("/api/faculty/profile")
def get_faculty_profile(request: Request):
    """Return the logged-in faculty's full profile."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.email, u.role, u.created_at,
                   f.qualification, f.specialization, f.experience_years
            FROM users u
            LEFT JOIN faculty f ON u.user_id = f.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        profile = cursor.fetchone()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        if profile.get('created_at'):
            profile['created_at'] = profile['created_at'].isoformat()

        return profile
    finally:
        cursor.close()
        conn.close()


# ── GET /api/faculty/dashboard-stats ─────────────────────────────────────────
@app.get("/api/faculty/dashboard-stats")
def get_faculty_dashboard_stats(request: Request):
    """Return stat card counts for the faculty dashboard."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        # Total approved resources
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE status = 'APPROVED'")
        total_resources = cursor.fetchone()['cnt']

        # Pending reviews (student submissions awaiting approval)
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE status = 'PENDING'")
        pending_reviews = cursor.fetchone()['cnt']

        # My uploads
        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE uploaded_by = %s", (user_id,))
        my_uploads = cursor.fetchone()['cnt']

        # Total notices
        cursor.execute("SELECT COUNT(*) as cnt FROM notices")
        total_notices = cursor.fetchone()['cnt']

        # Total subjects
        cursor.execute("SELECT COUNT(*) as cnt FROM subjects")
        total_subjects = cursor.fetchone()['cnt']

        # Total students
        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'STUDENT'")
        total_students = cursor.fetchone()['cnt']

        return {
            "total_resources": total_resources,
            "pending_reviews": pending_reviews,
            "my_uploads": my_uploads,
            "total_notices": total_notices,
            "total_subjects": total_subjects,
            "total_students": total_students
        }
    finally:
        cursor.close()
        conn.close()


# ── POST /api/faculty/upload ─────────────────────────────────────────────────
@app.post("/api/faculty/upload")
async def faculty_upload_resource(
    request: Request,
    title: str = Form(...),
    subject_id: int = Form(...),
    file_type: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):
    """Faculty upload — auto-APPROVED."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    allowed_exts = {'.pdf', '.ppt', '.pptx', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    conn = get_db_connection()
    if not conn:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO resources (title, description, file_path, file_type, uploaded_by, subject_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'APPROVED')
        """, (title, description, unique_name, file_type, user_id, subject_id))
        conn.commit()
        return {"message": "Resource uploaded and published successfully.", "resource_id": cursor.lastrowid}
    except Error as e:
        conn.rollback()
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── GET /api/faculty/pending-reviews ─────────────────────────────────────────
@app.get("/api/faculty/pending-reviews")
def get_pending_reviews(request: Request):
    """Return all PENDING resources for faculty review."""
    get_current_user(request)  # auth check

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.resource_id, r.title, r.description, r.file_path, r.file_type,
                   r.status, r.created_at,
                   u.full_name AS uploaded_by_name, u.role AS uploader_role,
                   sub.subject_code, sub.subject_name,
                   sem.semester_number
            FROM resources r
            JOIN users u ON r.uploaded_by = u.user_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            JOIN semesters sem ON sub.semester_id = sem.semester_id
            WHERE r.status = 'PENDING'
            ORDER BY r.created_at DESC
        """)
        resources = cursor.fetchall()

        for r in resources:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].isoformat()

        return resources
    finally:
        cursor.close()
        conn.close()


# ── PUT /api/faculty/review/{id} ─────────────────────────────────────────────
class ReviewAction(BaseModel):
    action: str  # "APPROVED" or "REJECTED"

@app.put("/api/faculty/review/{resource_id}")
def review_resource(resource_id: int, body: ReviewAction, request: Request):
    """Approve or reject a pending resource."""
    get_current_user(request)  # auth check

    if body.action not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Action must be 'APPROVED' or 'REJECTED'.")

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT resource_id, status FROM resources WHERE resource_id = %s", (resource_id,))
        resource = cursor.fetchone()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        cursor.execute("UPDATE resources SET status = %s WHERE resource_id = %s", (body.action, resource_id))
        conn.commit()
        return {"message": f"Resource {body.action.lower()} successfully."}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── POST /api/faculty/notice ─────────────────────────────────────────────────
class NoticeCreate(BaseModel):
    title: str
    content: str

@app.post("/api/faculty/notice")
def create_notice(body: NoticeCreate, request: Request):
    """Create a new department notice."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO notices (title, content, posted_by) VALUES (%s, %s, %s)",
            (body.title, body.content, user_id)
        )
        conn.commit()
        return {"message": "Notice posted successfully.", "notice_id": cursor.lastrowid}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── POST /api/faculty/subject ────────────────────────────────────────────────
class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    semester_number: int

@app.post("/api/faculty/subject")
def create_subject(body: SubjectCreate, request: Request):
    """Add a new subject to a semester."""
    user = get_current_user(request)  # auth check

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        # Get or create semester
        cursor.execute("SELECT semester_id FROM semesters WHERE semester_number = %s", (body.semester_number,))
        sem_row = cursor.fetchone()
        if not sem_row:
            cursor.execute("INSERT INTO semesters (semester_number) VALUES (%s)", (body.semester_number,))
            semester_id = cursor.lastrowid
        else:
            semester_id = sem_row['semester_id']

        # Check duplicate
        cursor.execute("SELECT subject_id FROM subjects WHERE subject_code = %s", (body.subject_code,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Subject code already exists.")

        cursor.execute(
            "INSERT INTO subjects (subject_code, subject_name, semester_id, created_by) VALUES (%s, %s, %s, %s)",
            (body.subject_code, body.subject_name, semester_id, int(user['sub']))
        )
        conn.commit()
        return {"message": "Subject added successfully.", "subject_id": cursor.lastrowid}
    except HTTPException:
        conn.rollback()
        raise
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── GET /api/faculty/my-subjects ─────────────────────────────────────────────
@app.get("/api/faculty/my-subjects")
def get_my_subjects(request: Request):
    """Return subjects created by the logged-in faculty."""
    user = get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sub.subject_id, sub.subject_code, sub.subject_name,
                   sem.semester_number
            FROM subjects sub
            JOIN semesters sem ON sub.semester_id = sem.semester_id
            WHERE sub.created_by = %s
            ORDER BY sem.semester_number, sub.subject_code
        """, (int(user['sub']),))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ── DELETE /api/faculty/notice/{id} ──────────────────────────────────────────
@app.delete("/api/faculty/notice/{notice_id}")
def delete_notice(notice_id: int, request: Request):
    """Delete a notice posted by this faculty."""
    user_data = get_current_user(request)
    user_id = int(user_data["sub"])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT notice_id, posted_by FROM notices WHERE notice_id = %s", (notice_id,))
        notice = cursor.fetchone()
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")
        if notice['posted_by'] != user_id:
            raise HTTPException(status_code=403, detail="You can only delete your own notices.")

        cursor.execute("DELETE FROM notices WHERE notice_id = %s", (notice_id,))
        conn.commit()
        return {"message": "Notice deleted successfully."}
    except HTTPException:
        raise
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /api/admin/dashboard-stats ───────────────────────────────────────────
@app.get("/api/admin/dashboard-stats")
def admin_dashboard_stats(request: Request):
    """Return stat card counts for the admin dashboard."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'STUDENT'")
        total_students = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'FACULTY'")
        total_faculty = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE status = 'APPROVED'")
        total_resources = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM resources WHERE status = 'PENDING'")
        pending_uploads = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM notices")
        total_notices = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM subjects")
        total_subjects = cursor.fetchone()['cnt']

        return {
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_resources": total_resources,
            "pending_uploads": pending_uploads,
            "total_notices": total_notices,
            "total_subjects": total_subjects,
        }
    finally:
        cursor.close()
        conn.close()


# ── GET /api/admin/users ─────────────────────────────────────────────────────
@app.get("/api/admin/users")
def admin_list_users(
    request: Request,
    role: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    """List all users with optional role filter and search."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT u.user_id, u.full_name, u.email, u.role, u.created_at,
                   s.usn,
                   f.qualification, f.specialization
            FROM users u
            LEFT JOIN students s ON u.user_id = s.user_id
            LEFT JOIN faculty f ON u.user_id = f.user_id
            WHERE 1=1
        """
        params = []

        if role:
            sql += " AND u.role = %s"
            params.append(role.upper())

        if q:
            sql += " AND (u.full_name LIKE %s OR u.email LIKE %s)"
            like = f"%{q}%"
            params.extend([like, like])

        sql += " ORDER BY u.created_at DESC"

        cursor.execute(sql, params)
        users = cursor.fetchall()

        for u in users:
            if u.get('created_at'):
                u['created_at'] = u['created_at'].isoformat()

        return users
    finally:
        cursor.close()
        conn.close()


# ── POST /api/admin/user ─────────────────────────────────────────────────────
class AdminCreateUser(BaseModel):
    full_name: str
    email: str
    password: str
    role: str  # STUDENT, FACULTY, ADMIN
    usn: Optional[str] = None
    semester_number: Optional[int] = None

@app.post("/api/admin/user")
def admin_create_user(body: AdminCreateUser, request: Request):
    """Admin creates a user of any role."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (body.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Email already registered.")

        hashed = hash_password(body.password)
        role = body.role.upper()
        if role not in ("STUDENT", "FACULTY", "ADMIN"):
            raise HTTPException(status_code=400, detail="Invalid role.")

        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (body.full_name, body.email, hashed, role)
        )
        user_id = cursor.lastrowid

        if role == "STUDENT" and body.usn:
            sem_id = None
            if body.semester_number:
                cursor.execute("SELECT semester_id FROM semesters WHERE semester_number = %s", (body.semester_number,))
                row = cursor.fetchone()
                if row:
                    sem_id = row['semester_id']
                else:
                    cursor.execute("INSERT INTO semesters (semester_number) VALUES (%s)", (body.semester_number,))
                    sem_id = cursor.lastrowid
            if sem_id:
                cursor.execute("INSERT INTO students (user_id, usn, semester_id) VALUES (%s, %s, %s)", (user_id, body.usn, sem_id))

        if role == "FACULTY":
            cursor.execute("INSERT INTO faculty (user_id) VALUES (%s)", (user_id,))

        conn.commit()
        return {"message": f"User '{body.full_name}' created as {role}.", "user_id": user_id}
    except HTTPException:
        conn.rollback()
        raise
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── DELETE /api/admin/user/{id} ──────────────────────────────────────────────
@app.delete("/api/admin/user/{user_id}")
def admin_delete_user(user_id: int, request: Request):
    """Delete a user (cascades to student/faculty tables)."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return {"message": "User deleted successfully."}
    except HTTPException:
        raise
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ── GET /api/admin/all-resources ─────────────────────────────────────────────
@app.get("/api/admin/all-resources")
def admin_all_resources(request: Request):
    """Return all resources regardless of status."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.resource_id, r.title, r.description, r.file_path, r.file_type,
                   r.status, r.created_at,
                   u.full_name AS uploaded_by_name,
                   sub.subject_code, sub.subject_name,
                   sem.semester_number
            FROM resources r
            JOIN users u ON r.uploaded_by = u.user_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            JOIN semesters sem ON sub.semester_id = sem.semester_id
            ORDER BY r.created_at DESC
        """)
        resources = cursor.fetchall()

        for r in resources:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].isoformat()

        return resources
    finally:
        cursor.close()
        conn.close()


# ── DELETE /api/admin/resource/{id} ──────────────────────────────────────────
@app.delete("/api/admin/resource/{resource_id}")
def admin_delete_resource(resource_id: int, request: Request):
    """Delete a resource and its file."""
    get_current_user(request)

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT resource_id, file_path FROM resources WHERE resource_id = %s", (resource_id,))
        resource = cursor.fetchone()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        cursor.execute("DELETE FROM resources WHERE resource_id = %s", (resource_id,))
        conn.commit()

        # Remove file
        fp = os.path.join(UPLOAD_DIR, resource['file_path'])
        if os.path.exists(fp):
            os.remove(fp)

        return {"message": "Resource deleted successfully."}
    except HTTPException:
        raise
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@app.post("/api/admin/bulk-upload")
async def admin_bulk_upload(request: Request, file: UploadFile = File(...)):
    """Bulk-create student users from a CSV file."""
    get_current_user(request)

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        text = contents.decode('utf-8')
    except UnicodeDecodeError:
        text = contents.decode('latin-1')

    reader = csv.DictReader(io.StringIO(text))
    required = {'full_name', 'email', 'usn', 'semester_number', 'password'}
    if not required.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have columns: {', '.join(sorted(required))}. Got: {', '.join(reader.fieldnames or [])}"
        )

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    results = []
    success_count = 0
    error_count = 0

    try:
        for i, row in enumerate(reader, start=2):  # row 1 is header
            name  = (row.get('full_name') or '').strip()
            email = (row.get('email') or '').strip()
            usn   = (row.get('usn') or '').strip()
            sem   = (row.get('semester_number') or '').strip()
            pwd   = (row.get('password') or '').strip()
            phone = (row.get('phone') or '').strip()

            if not all([name, email, usn, sem, pwd]):
                results.append({"row": i, "email": email or '(empty)', "status": "error", "detail": "Missing required fields"})
                error_count += 1
                continue

            try:
                sem_num = int(sem)
            except ValueError:
                results.append({"row": i, "email": email, "status": "error", "detail": "Invalid semester number"})
                error_count += 1
                continue

            # Check duplicates
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                results.append({"row": i, "email": email, "status": "error", "detail": "Email already registered"})
                error_count += 1
                continue

            cursor.execute("SELECT user_id FROM students WHERE usn = %s", (usn,))
            if cursor.fetchone():
                results.append({"row": i, "email": email, "status": "error", "detail": f"USN {usn} already registered"})
                error_count += 1
                continue

            # Get or create semester
            cursor.execute("SELECT semester_id FROM semesters WHERE semester_number = %s", (sem_num,))
            sem_row = cursor.fetchone()
            if sem_row:
                semester_id = sem_row['semester_id']
            else:
                cursor.execute("INSERT INTO semesters (semester_number) VALUES (%s)", (sem_num,))
                semester_id = cursor.lastrowid

            # Create user
            hashed = hash_password(pwd)
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'STUDENT')",
                (name, email, hashed)
            )
            user_id = cursor.lastrowid

            # Create student entry
            cursor.execute(
                "INSERT INTO students (user_id, usn, semester_id) VALUES (%s, %s, %s)",
                (user_id, usn, semester_id)
            )

            results.append({"row": i, "email": email, "status": "success", "detail": f"Created as STUDENT (Sem {sem_num})"})
            success_count += 1

        conn.commit()
        return {
            "message": f"{success_count} users created, {error_count} errors.",
            "success": success_count,
            "errors": error_count,
            "details": results
        }
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@app.get("/api/admin/bulk-template")
async def download_bulk_template():
    """Serve the CSV template for bulk upload."""
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students_template.csv")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template file not found.")
    return FileResponse(template_path, filename="students_template.csv", media_type="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
#  FORGOT / RESET PASSWORD
# ══════════════════════════════════════════════════════════════════════════════

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str


def _send_otp_email(to_email: str, otp: str, user_name: str):
    """Send a password-reset OTP via Gmail SMTP."""
    if not SMTP_EMAIL or not SMTP_APP_PASS:
        raise HTTPException(status_code=500, detail="Email service not configured.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "EduCoreHub – Password Reset OTP"
    msg["From"]    = f"EduCoreHub <{SMTP_EMAIL}>"
    msg["To"]      = to_email

    html = f"""\
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;background:#0d0f18;color:#e8eaf6;border-radius:16px;border:1px solid rgba(108,99,255,.25)">
      <h2 style="margin:0 0 8px;color:#9d97ff">Password Reset</h2>
      <p style="margin:0 0 24px;color:#8b90b5;font-size:14px">Hi {user_name}, use the OTP below to reset your password. It expires in <b>10 minutes</b>.</p>
      <div style="text-align:center;padding:20px;background:#13172a;border-radius:12px;border:1px solid rgba(108,99,255,.2);letter-spacing:8px;font-size:32px;font-weight:700;color:#6c63ff">{otp}</div>
      <p style="margin:24px 0 0;color:#8b90b5;font-size:12px">If you did not request this, please ignore this email.</p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_APP_PASS)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.post("/api/forgot-password")
def forgot_password(body: ForgotPasswordRequest):
    """Generate a 6-digit OTP and email it to the user."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, full_name, role FROM users WHERE email = %s", (body.email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with this email.")

        if user["role"] == "ADMIN":
            raise HTTPException(status_code=403, detail="Admin password reset is not allowed via email. Contact the system administrator.")

        otp = str(random.randint(100000, 999999))
        password_reset_otps[body.email] = {
            "otp": otp,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }

        _send_otp_email(body.email, otp, user["full_name"])
        return {"message": "OTP sent to your email address."}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/reset-password")
def reset_password(body: ResetPasswordRequest):
    """Verify OTP and update the user's password."""
    stored = password_reset_otps.get(body.email)
    if not stored:
        raise HTTPException(status_code=400, detail="No OTP requested for this email. Please request a new one.")

    if datetime.now(timezone.utc) > stored["expires_at"]:
        password_reset_otps.pop(body.email, None)
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if stored["otp"] != body.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    # OTP valid – update password
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    try:
        hashed = hash_password(body.new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed, body.email))
        conn.commit()
        password_reset_otps.pop(body.email, None)
        return {"message": "Password reset successfully. You can now log in with your new password."}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
