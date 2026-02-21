import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''  # XAMPP default
    )

    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS educorehub")
    cursor.execute("USE educorehub")

    # 1️⃣ USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('ADMIN','FACULTY','STUDENT') NOT NULL,
        department VARCHAR(100) DEFAULT NULL,
        phone VARCHAR(20) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)
    print("✅ Users table created")

    # 2️⃣ SEMESTERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semesters (
        semester_id INT PRIMARY KEY AUTO_INCREMENT,
        semester_number INT UNIQUE NOT NULL
    ) ENGINE=InnoDB;
    """)
    print("✅ Semesters table created")

    # 3️⃣ STUDENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        user_id INT NOT NULL,
        usn VARCHAR(20) UNIQUE NOT NULL,
        semester_id INT NOT NULL,
        PRIMARY KEY (user_id),
        FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE,
        FOREIGN KEY (semester_id)
            REFERENCES semesters(semester_id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)
    print("✅ Students table created")

    # 4️⃣ FACULTY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        user_id INT NOT NULL,
        qualification VARCHAR(100),
        specialization VARCHAR(100),
        experience_years INT,
        PRIMARY KEY (user_id),
        FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)
    print("✅ Faculty table created")

    # 5️⃣ SUBJECTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INT PRIMARY KEY AUTO_INCREMENT,
        subject_code VARCHAR(20) UNIQUE NOT NULL,
        subject_name VARCHAR(100) NOT NULL,
        semester_id INT NOT NULL,
        created_by INT,
        FOREIGN KEY (semester_id)
            REFERENCES semesters(semester_id)
            ON DELETE CASCADE,
        FOREIGN KEY (created_by)
            REFERENCES users(user_id)
            ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """)
    print("✅ Subjects table created")

    # 6️⃣ RESOURCES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        resource_id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        file_path VARCHAR(500),
        file_type ENUM('PDF','PPT','DOC','IMAGE','URL') NOT NULL,
        uploaded_by INT NOT NULL,
        subject_id INT NOT NULL,
        status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uploaded_by)
            REFERENCES users(user_id)
            ON DELETE CASCADE,
        FOREIGN KEY (subject_id)
            REFERENCES subjects(subject_id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)
    print("✅ Resources table created")

    # 7️⃣ NOTICES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        notice_id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        target_audience VARCHAR(100) DEFAULT 'ALL',
        posted_by INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (posted_by)
            REFERENCES users(user_id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)
    print("✅ Notices table created")

except Error as e:
    print("❌ Error:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("🔒 MySQL connection closed.")