from database import get_db_connection

connection  = get_db_connection()

connection.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        location TEXT,
        latitude REAL,
        longitude REAL,
        condition TEXT,
        priority TEXT,
        entry_date TEXT,
        exit_date TEXT
    )
""")

connection.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    emergency_availablity INTEGER DEFAULT 1 
    )
""")

connection.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
    )
""")

connection.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        generic_name TEXT,
        composition TEXT,
        stock INTEGER DEFAULT 0,
        hospital_id INTEGER,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
    )
""")

connection.execute("DELETE FROM patients")
connection.execute("DELETE FROM hospitals")
connection.execute("DELETE FROM users")
connection.execute("DELETE FROM medicines")

medicines = [
    (
        "Paracetamol 500mg",
        "Paracetamol",
        "Paracetamol",
        120,
        1
    ),
    (
        "Amoxicillin 500mg",
        "Amoxicillin",
        "Amoxicillin",
        50,
        1
    ),
    (
        "Ibuprofen 400mg",
        "Ibuprofen",
        "Ibuprofen",
        0,
        2
    ),
    (
        "Cetirizine 10mg",
        "Cetirizine",
        "Cetirizine",
        80,
        2
    ),
    (
        "ORS",
        "Oral Rehydration Salts",
        "Sodium chloride + potassium chloride + glucose",
        35,
        3
    )
]

users = [
    ("patient01", "demo123", "patient"),
    ("staff01", "demo123", "staff"),
    ("visitor01", "demo123", "visitor")
]

patients = [
    (
        "Abc Sen",
        56,
        "Agarpara",
        22.683215,
        88.391812,
        "Chest pain",
        "Emergency",
        "2026-09-08",
        None
    ),
    (
        "Jkl Sharma",
        32,
        "North DumDum",
        22.664960,
        88.422411,
        "Fever",
        "Normal",
        "2026-09-07",
        None
    ),
    (
        "Xyz Roy",
        67,
        "Barrackpore",
        22.963112,
        88.392585,
        "Breathing difficulty",
        "Emergency",
        "2026-09-08",
        None
    )    
]

hospitals = [
    (
        "GHI Hospital",
        "Barrackpore Trunk Rd, Rathtala",
        22.663095,
        88.37692,
        1
    ),
    (
        "DEF Hospital",
        "Nilgunj Rd, Agarpara",
        22.68318,
        88.378723,
        1
    ),
    (
        "JKL Hospital",
        "Panihati",
        22.692423,
        88.39767,
        0
    ),
    (
        "MNO Hospital",
        "Rathtala",
        22.665814,
        88.376942,
        1
    ),
    (
        "PQR Hospital",
        "Netai Pally",
        22.694715,
        88.406982,
        1
    )
]

connection.executemany("""
    INSERT INTO medicines
    (
        name,
        generic_name,
        composition,
        stock,
        hospital_id
    )
    VALUES (?, ?, ?, ?, ?)
""", medicines)

connection.executemany("""
    INSERT INTO users
    (username, password, role)
    VALUES (?, ?, ?)
""", users)

connection.executemany("""
 INSERT INTO patients
 (name, age, location, latitude, longitude, condition, priority, entry_date, exit_date)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", patients)

connection.executemany("""
     INSERT INTO hospitals
     (name, address, latitude, longitude, emergency_availablity)
     VALUES (?, ?, ?, ?, ?)
""", hospitals)

connection.commit()
connection.close()

print("Database is ok")
# adding this just so git commits

