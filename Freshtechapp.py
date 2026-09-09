import math
from flask import Flask, jsonify, request
from database import get_db_connection

#calcing distance by Havensine formula
def dist(lat1, lon1, lat2, lon2):
    R = 6371 

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

    return R*c 

Emergency_conditions = {
    "chest pain",
    "breathing difficulty",
    "unconscious",
    "bleeding",
}

def determine_priority(condition):
    condition = condition.strip().lower()

    if condition in Emergency_conditions:
        return "Emergency"
    return "Normal"

app = Flask(__name__)

@app.route("/")
def home():
    return "FreshTech backend is ok"

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error":"Request body is required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    connection = get_db_connection()

    user = connection.execute("""
        SELECT id, username, role
        FROM users
        WHERE username = ? AND password = ?
    """, (username, password)).fetchone()

    connection.close()

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({
        "success": True,
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"]
    })

@app.route("/api/patients")
def get_patients():
    connection = get_db_connection()

    patients = connection.execute("SELECT * FROM patients").fetchall()
    connection.close()

    return jsonify([dict(patient) for patient in patients])

@app.route("/api/hospitals")
def get_hospitals():
    connection = get_db_connection()

    hospitals = connection.execute("SELECT * FROM hospitals").fetchall()
    connection.close()

    return jsonify([dict(hospital) for hospital in hospitals])

@app.route("/api/patients/<int:patient_id>")
def get_patient(patient_id):
    connection = get_db_connection()

    patient = connection.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,),
    ).fetchone()

    connection.close()

    if patient is None:
        return jsonify ({"error": "Patient not found"}), 404

    return jsonify (dict(patient))

@app.route("/api/patients/<int:patient_id>/nearhospital")
def get_near_hospital(patient_id):
    connection = get_db_connection()

    patient = connection.execute( "SELECT * FROM patients WHERE id = ?",(patient_id,)).fetchone()
    
    if patient is None:
        connection.close()
        return jsonify({"error": "Patient not found"}), 404

    if patient["latitude"] is None or patient["longitude"] is None:
        connection.close()
        return jsonify({"error": "Entering location is required"}), 400

    hospitals = connection.execute("SELECT * FROM hospitals").fetchall()
    connection.close()


    near_hospital = []

    for hospital in hospitals:
        distance = dist(
            patient["latitude"],
            patient["longitude"],
            hospital["latitude"],
            hospital["longitude"],
        )
        near_hospital.append(
            {
                "id": hospital["id"],
                "name": hospital["name"],
                "address": hospital["address"],
                "distance_km": round(distance, 2),
                "emergency_available": bool(hospital["emergency_availablity"]),
            }
        )

    near_hospital.sort(key=lambda hospital: hospital["distance_km"])
    return jsonify(near_hospital)   

@app.route("/api/emergency", methods=["POST"])
def create_emergency():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    patient_id = data.get("patient_id")
    condition = data.get("condition")

    if patient_id is None or not condition:
        return jsonify({"error": "patient_id and condition are required"}), 400

    priority = determine_priority(condition)

    connection = get_db_connection()

    patient = connection.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,),
    ).fetchone()

    if patient is None:
        connection.close()
        return jsonify({"error": "Patient not found"}), 400

    connection.execute("""
     UPDATE patients
     SET condition = ?, priority = ?
     WHERE id = ?
""", (condition, priority, patient_id))

    connection.commit()
    connection.close()

    return jsonify(
        {
            "patient_id": patient_id,
            "condition": condition,
            "priority": priority,
        }
    )

@app.route("/api/queue")
def get_queue():
    connection = get_db_connection()

    patients = connection.execute("""
        SELECT * FROM patients
        ORDER BY CASE WHEN priority = 'Emergency' THEN 0 ELSE 1 END,
        entry_date ASC,
        id ASC
        """).fetchall()

    connection.close()

    queue = []

    for index, patient in enumerate(patients, start=1):
        queue.append(
            {
                "queue_position": index,
                "patient_id": patient["id"],
                "name": patient["name"],
                "priority": patient["priority"],
                "condition": patient["condition"],
            }
        )

    return jsonify(queue)

@app.route("/api/medicines/search")
def search_medicines():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Search query is required"
        }), 400

    connection = get_db_connection()

    medicines = connection.execute("""
        SELECT
            medicines.id,
            medicines.name,
            medicines.generic_name,
            medicines.composition,
            medicines.stock,
            hospitals.name AS hospital
        FROM medicines
        JOIN hospitals
            ON medicines.hospital_id = hospitals.id
        WHERE
            medicines.name LIKE ?
            OR medicines.generic_name LIKE ?
            OR medicines.composition LIKE ?
    """, (
        f"%{query}%",
        f"%{query}%",
        f"%{query}%"
    )).fetchall()

    connection.close()

    results = []

    for medicine in medicines:
        results.append({
            "id": medicine["id"],
            "name": medicine["name"],
            "generic_name": medicine["generic_name"],
            "composition": medicine["composition"],
            "hospital": medicine["hospital"],
            "stock": medicine["stock"],
            "available": medicine["stock"] > 0
        })

    return jsonify(results)



@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "FreshTech backend"
    })

if __name__ == "__main__":
    app.run(debug=True)
