
from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime
from contextlib import contextmanager
import sqlite3

app = Flask(__name__)
DATABASE = "parking.db"


@contextmanager
def db_connection():
    """Open a database connection and always close it."""
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create the parking database table if it does not exist."""
    with db_connection() as conn:
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

    <title>Parking Management System - v2</title>

    <style>
        * {
            box-sizing: border-box;
        }

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

        h1 {
            color: #1d4ed8;
        }

        h2 {
            margin-top: 28px;
        }

        label {
            display: block;
            margin-top: 16px;
            font-weight: bold;
        }

        input, select, button {
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
            margin-top: 18px;
        }

        button:hover {
            background: #1d4ed8;
        }

        .exit-button {
            background: #0f766e;
        }

        .exit-button:hover {
            background: #115e59;
        }

        .notice {
            background: #dcfce7;
            color: #166534;
            padding: 12px;
            border-radius: 6px;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 12px;
            border-radius: 6px;
        }

        .subtitle {
            color: #64748b;
        }

        hr {
            border: 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 28px;
        }
    </style>
</head>

<body>
    <main class="container">
        <h1>Parking Management System</h1>

        <p class="subtitle">
            Version 2 | Vehicle Entry and Exit Management
        </p>

        {% if message %}
            <p class="notice">{{ message }}</p>
        {% endif %}

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <h2>Add Vehicle</h2>

        <form method="POST" action="{{ url_for('add_vehicle') }}">
            <label for="vehicle_number">
                Vehicle Registration Number
            </label>

            <input
                id="vehicle_number"
                name="vehicle_number"
                placeholder="e.g. TN01AB1234"
                maxlength="20"
                required
            >

            <label for="vehicle_type">Vehicle Type</label>

            <select id="vehicle_type" name="vehicle_type" required>
                <option value="Car">Car</option>
                <option value="Bike">Bike</option>
                <option value="Scooter">Scooter</option>
                <option value="Van">Van</option>
                <option value="Truck">Truck</option>
            </select>

            <button type="submit">
                Record Vehicle Entry
            </button>
        </form>

        <hr>

        <h2>Exit Vehicle</h2>

        <form method="POST" action="{{ url_for('exit_vehicle') }}">
            <label for="exit_vehicle_number">
                Vehicle Registration Number
            </label>

            <input
                id="exit_vehicle_number"
                name="vehicle_number"
                placeholder="Enter registered vehicle number"
                maxlength="20"
                required
            >

            <button class="exit-button" type="submit">
                Record Vehicle Exit
            </button>
        </form>
    </main>
</body>
</html>
"""


def render_page(message=None, error=None, status=200):
    return (
        render_template_string(
            PAGE,
            message=message,
            error=error,
        ),
        status,
    )


@app.route("/")
def home():
    return render_page()


@app.route("/add", methods=["POST"])
def add_vehicle():
    vehicle_number = request.form.get(
        "vehicle_number", ""
    ).strip().upper()

    vehicle_type = request.form.get(
        "vehicle_type", ""
    ).strip()

    allowed_types = {
        "Car", "Bike", "Scooter", "Van", "Truck"
    }

    if not vehicle_number or vehicle_type not in allowed_types:
        return render_page(
            error="Invalid vehicle details.",
            status=400,
        )

    entry_time = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO vehicles
                (vehicle_number, vehicle_type, entry_time)
            VALUES (?, ?, ?)
            """,
            (vehicle_number, vehicle_type, entry_time),
        )

    return render_page(
        message="Vehicle entry recorded successfully!"
    )


@app.route("/exit", methods=["POST"])
def exit_vehicle():
    vehicle_number = request.form.get(
        "vehicle_number", ""
    ).strip().upper()

    if not vehicle_number:
        return render_page(
            error="Enter a vehicle number.",
            status=400,
        )

    exit_time = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with db_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE vehicles
            SET exit_time = ?
            WHERE id = (
                SELECT id
                FROM vehicles
                WHERE vehicle_number = ?
                  AND exit_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            )
            """,
            (exit_time, vehicle_number),
        )

        updated = cursor.rowcount

    if updated == 0:
        return render_page(
            error="No active parking entry found for this vehicle.",
            status=404,
        )

    return render_page(
        message="Vehicle exit recorded successfully!"
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
