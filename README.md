# EduCoreHub 🎓
**Departmental Digital Resource & Knowledge Hub**

A comprehensive, robust, and beautifully designed web platform built specifically for academic departments. It serves as a centralized hub for study material sharing, official communications, and administration, seamlessly connecting Students, Faculty, and Administrators.

---

## 🌟 Comprehensive Feature List

### � Authentication & Security
* **Role-Based Access Control (RBAC)**: Distinct, isolated dashboards for Students, Faculty, and Administrators.
* **JSON Web Tokens (JWT)**: Secure, stateless authentication enforcing expiration times and access limits.
* **Frontend Route Guards**: Unauthenticated users are strictly rebounded back to the login page when attempting to access restricted URLs.
* **Encrypted Passwords**: `bcrypt` implementation protecting all sensitive credentials in the database.
* **Multi-Portal Access**: Dedicated entry points (e.g., General Login, Faculty Login, Admin Portal).
* **Forgot Password flow**: Designed with email OTP verification and new password creation steps.
* **Registration Validation**: Strict form validation handling duplicates (Email & USN uniqueness checks).

### 💅 Modern User Interface & Aesthetics
* **Dual Themes**: Instant Dark Mode / Light Mode toggle entirely preserved across browsing sessions.
* **Premium Typography**: Built utilizing modern Google Fonts (`Outfit` for crisp headers, `DM Sans` for readable body text).
* **Glassmorphism UI**: Beautiful, semi-transparent frosted glass design elements and hover interactions.
* **Responsive Architecture**: Fully mobile-optimized layouts with an off-canvas mobile navigation sidebar.
* **Micro-Animations**: Shimmer loading states, smooth counting counters, drop-down fades, and button transitions out of the box.
* **Custom Dropdowns**: Beautiful profile details and notification popovers accessible from the navigational topbar.

### � AI Integration
* **Grammar Check Assistant**: An "AI Check" feature integrated into every editor (Notice Boards, Upload Descriptions). Employs the LanguageTool API to instantly scan paragraphs and replace spelling/grammar mistakes automatically with visual feedback.

### 🎓 1. Student Portal 
* **Personalized Dashboard**: A welcome greeting showcasing active stats for the semester.
* **Browse Resources**: Instantly filter hundreds of study materials by **Keyword, Subject, Semester, or File Type** (PDF, PPT, DOC, Image). Download files directly.
* **File Uploads**: Students can upload their own notes and assignments to the ecosystem. These files enter a "Pending Review" queue to be vetted by faculty before publishing.
* **My Uploads**: A personal table tracking the approval status (Pending/Approved/Rejected) of personal contributions.
* **Notice Board**: Read official announcements, filter notices by keywords, and easily spot new circulars.
* **Profile**: View detailed personal academic information (USN, Joined Date, specific Semester).

### 👨‍🏫 2. Faculty Portal
* **Review Queue**: Quality control mechanism to Approve or Reject student resource uploads directly from the dashboard interface with single-click actions.
* **Direct Resource Publishing**: Faculty uploads bypass the review queue and are instantly published to the department.
* **Manage Subjects Framework**: Faculty members can create, update, or remove subjects (including matching them to semesters) that dynamically updates the dropdown menus across the whole system.
* **Rich Notice Editor**: Create comprehensive notices with text formatting. Includes features to toggle **Pinning** to the top of boards or inputting future **Scheduled Dates**.
* **Notice Management**: Keep track of a chronological notice timeline. Individual faculty can confidently delete the notices they have published previously.
* **Stat Dashboard**: Monitor platform growth highlighting total resources, personal uploads, pending reviews, and active notices.

### 🛡️ 3. Admin Control Center
* **Complete User Management (CRUD)**: Table listing every Student, Faculty, or Admin. Filter users by role, search by name/email, and manually delete or manually create any individual user overriding standard controls.
* **Bulk Data Importation**: Import hundreds of users in seconds using CSV Excel files. Features an intuitive drag-and-drop interface, upload progression bars, and row-by-row error reporting validation.
* **Global Review Authority**: Admins see all pending reviews across the entire platform and possess global Approve/Reject abilities comparable to faculty.
* **Global Resource Management**: Admin oversight panel to view every file uploaded to the server. Advanced filtering, native direct file uploads via modal, and instant deletion powers.
* **Global Notice Management**: A centralized hub giving the Admin unrestricted powers to post new circulars or forcefully delete any notice published by anyone on the platform.
* **Advanced Analytics**: Granular metric modules displaying the total students enrolled, total active faculty, available library resources, and pending activities across all users. 

---

## 🛠️ Technology Stack
* **Frontend Structure**: HTML5 layout without heavy single-page application framework bloat.
* **Styling**: Vanilla CSS utilizing custom variables, grids, flexboxes, and pseudo-elements.
* **Interactivity**: Vanilla JavaScript `fetch` architecture managing asynchronous communication with the server.
* **Backend Framework**: Python FastAPI producing highly efficient, concurrent RESTful APIs with automatic documentation (Swagger UI).
* **Database Management**: Dedicated MySQL database managing multiple robust, relational interconnected tables (`users`, `resources`, `subjects`, `notices`, `semesters`).
* **File System**: Secure backend file routing managing binary storage logic for PDFs, Images, and Documents directly via local directory saving.

---

## 📦 Setup & Installation Guide

1. Navigate to the absolute `backend` directory.
2. Install Python backend dependencies:
   ```bash
   pip install fastapi uvicorn mysql-connector-python pyjwt passlib bcrypt python-multipart
   ```
3. Boot up your MySQL Server and prepare matching credentials. Update `.env` or internal script constants with the appropriate Username and Password.
4. Run the schema creation script to scaffold the clean database tables:
   ```bash
   python MysqlCreator.py
   ```
5. Seed initial placeholder subjects and the super-user faculty/admin accounts:
   ```bash
   python seed_faculty_admin.py
   ```
6. Start the ASGI server (automatically reloads on changes):
   ```bash
   uvicorn main:app --reload
   ```
7. Fire up your preferred web browser and direct it to `http://127.0.0.1:8000/login` to access the full portal suite. Ensure you login via `/admin/login` or `/faculty/login` for specific escalated privileges.
