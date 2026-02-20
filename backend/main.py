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
from datetime import datetime, timedelta, timezone

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
                   u.full_name AS posted_by
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
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
