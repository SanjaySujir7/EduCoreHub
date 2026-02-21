"""
seed_faculty_admin.py
─────────────────────
Inserts Faculty and Admin users into the EduCoreHub MySQL database
with bcrypt-hashed passwords.

Usage:
    python seed_faculty_admin.py

Requirements:
    pip install mysql-connector-python bcrypt
"""

import mysql.connector
from mysql.connector import Error
import bcrypt


# ── Configuration ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # XAMPP default
    "database": "educorehub",
}

# ── Sample Data ──────────────────────────────────────────────────────────────
# Add or modify entries below before running the script.

FACULTY_DATA = [
    {
        "full_name": "Praveen Kulakarni",
        "email": "praveen.kulakarni@educorehub.com",
        "password": "Faculty@123",
        "qualification": "Mca",
        "specialization": "Java",
        "experience_years": 15,
    },
    {
        "full_name": "Akshatha Marathe",
        "email": "akshatha.marathe@educorehub.com",
        "password": "Faculty@123",
        "qualification": "MSE",
        "specialization": "Digital Marketing",
        "experience_years": 15,
    },
    {
        "full_name": "Rahul",
        "email": "rahul@educorehub.com",
        "password": "Faculty@123",
        "qualification": "MCom",
        "specialization": "Finance",
        "experience_years": 12,
    },
]

ADMIN_DATA = [
    {
        "full_name": "Sanjay Sujir",
        "email": "admin@educorehub.com",
        "password": "admin@123",
    }
]


# ── Helper ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        print("✅ Connected to MySQL database 'educorehub'\n")

        # ── Insert Faculty ───────────────────────────────────────────────────
        print("─── Adding Faculty ─────────────────────────────────")
        for fac in FACULTY_DATA:
            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (fac["email"],))
            existing = cursor.fetchone()
            if existing:
                print(f"  ⚠️  Skipped (already exists): {fac['email']}")
                continue

            hashed_pw = hash_password(fac["password"])

            # Insert into users table
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, role) "
                "VALUES (%s, %s, %s, 'FACULTY')",
                (fac["full_name"], fac["email"], hashed_pw),
            )
            user_id = cursor.lastrowid

            # Insert into faculty table
            cursor.execute(
                "INSERT INTO faculty (user_id, qualification, specialization, experience_years) "
                "VALUES (%s, %s, %s, %s)",
                (user_id, fac["qualification"], fac["specialization"], fac["experience_years"]),
            )
            print(f"  ✅ Added faculty: {fac['full_name']} ({fac['email']})")

        # ── Insert Admins ────────────────────────────────────────────────────
        print("\n─── Adding Admins ──────────────────────────────────")
        for adm in ADMIN_DATA:
            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (adm["email"],))
            existing = cursor.fetchone()
            if existing:
                print(f"  ⚠️  Skipped (already exists): {adm['email']}")
                continue

            hashed_pw = hash_password(adm["password"])

            # Insert into users table
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, role) "
                "VALUES (%s, %s, %s, 'ADMIN')",
                (adm["full_name"], adm["email"], hashed_pw),
            )
            print(f"  ✅ Added admin : {adm['full_name']} ({adm['email']})")

        conn.commit()
        print("\n🎉 All data committed successfully!")

        # ── Summary ──────────────────────────────────────────────────────────
        print("\n─── Login Credentials ──────────────────────────────")
        print(f"{'Role':<10} {'Email':<35} {'Password':<15}")
        print("─" * 60)
        for fac in FACULTY_DATA:
            print(f"{'FACULTY':<10} {fac['email']:<35} {fac['password']:<15}")
        for adm in ADMIN_DATA:
            print(f"{'ADMIN':<10} {adm['email']:<35} {adm['password']:<15}")

    except Error as e:
        print(f"❌ MySQL Error: {e}")
        if conn and conn.is_connected():
            conn.rollback()

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n🔒 MySQL connection closed.")


if __name__ == "__main__":
    main()
