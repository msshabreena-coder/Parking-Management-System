
from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime
import sqlite3

app = Flask(__name__)
DATABASE = "parking.db"


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_number TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT
            )
        """)


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Parking Management System - v1</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
            color: #1e293b;
        }
        .container {
            max-width: 650px;
            margin: 30px auto;
            background: white;
            padding: 28px;
            border-radius: 12px;
            box-shadow: 0 4px 16px #00000012;
        }
        h1 { color: #1d4ed8; }
        label { display: block; margin-top: 18px; font-weight: bold; }
        input, select, button {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            font-size: 15px;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 22px;
        }
        button:hover { background: #1d4ed8; }
        .notice {
            background: #dcfce7;
            color: #166534;
            padding: 12px;
            border-radius: 6px;
        }
        .subtitle { color: #64748b; }
    </style>
</head>
<body>
    <main class="container">
        <h1>Parking Management System</h1>
        <p class="subtitle">Version 1 | Vehicle Entry Registration</p>

        {% if message %}
            <p class="notice">{{ message }}</p>
        {% endif %}

        <h2>Add Vehicle</h2>
        <form method="POST" action="{{ url_for('add_vehicle') }}">
            <label for="vehicle_number">Vehicle Registration Number</label>
            <input id="vehicle_number" name="vehicle_number"
                   placeholder="e.g. TN01AB1234" required maxlength="20">

            <label for="vehicle_type">Vehicle Type</label>
            <select id="vehicle_type" name="vehicle_type" required>
                <option value="Car">Car</option>
                <option value="Bike">Bike</option>
                <option value="Scooter">Scooter</option>
                <option value="Van">Van</option>
                <option value="Truck">Truck</option>
            </select>

            <button type="submit">Record Vehicle Entry</button>
        </form>
    </main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE, message=None)


@app.route("/add", methods=["POST"])
def add_vehicle():
    vehicle_number = request.form.get(
        "vehicle_number", ""
    ).strip().upper()
    vehicle_type = request.form.get("vehicle_type", "").strip()

    allowed_types = {"Car", "Bike", "Scooter", "Van", "Truck"}

    if not vehicle_number or vehicle_type not in allowed_types:
        return "Invalid vehicle details.", 400

    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            INSERT INTO vehicles
            (vehicle_number, vehicle_type, entry_time)
            VALUES (?, ?, ?)
            """,
            (
                vehicle_number,
                vehicle_type,
                datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
            ),
        )

    return redirect(url_for("success"))


@app.route("/success")
def success():
    return render_template_string(
        PAGE, message="Vehicle entry recorded successfully!"
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
