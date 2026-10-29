
from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime
from contextlib import contextmanager
import sqlite3

app = Flask(__name__)
DATABASE = "parking.db"


@contextmanager
def db_connection():
    """Manage SQLite connections safely."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create the vehicle table."""
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

    <title>Parking Management System - v3</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
            margin: 0;
            padding: 24px;
        }

        .container {
            max-width: 1050px;
            margin: 20px auto;
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

        .subtitle {
            color: #64748b;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }

        label {
            display: block;
            margin-top: 12px;
            font-weight: bold;
        }

        input, select, button {
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 15px;
        }

        button, .button-link {
            display: inline-block;
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 6px;
            text-decoration: none;
            cursor: pointer;
            margin-top: 18px;
        }

        button:hover, .button-link:hover {
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

        .table-wrapper {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 14px;
        }

        th, td {
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: #eff6ff;
            color: #1e40af;
        }

        tr:nth-child(even) {
            background: #f8fafc;
        }

        .status {
            font-weight: bold;
        }

        .active {
            color: #047857;
        }

        .exited {
            color: #64748b;
        }

        .empty {
            color: #64748b;
            padding: 16px 0;
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
        Version 3 | Vehicle Entry, Exit and Parking History
    </p>

    {% if message %}
        <p class="notice">{{ message }}</p>
    {% endif %}

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <h2>Add Vehicle</h2>

    <form method="POST" action="{{ url_for('add_vehicle') }}">
        <div class="form-grid">
            <div>
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
            </div>

            <div>
                <label for="vehicle_type">Vehicle Type</label>
                <select id="vehicle_type" name="vehicle_type" required>
                    <option value="Car">Car</option>
                    <option value="Bike">Bike</option>
                    <option value="Scooter">Scooter</option>
                    <option value="Van">Van</option>
                    <option value="Truck">Truck</option>
                </select>
            </div>
        </div>

        <button type="submit">Record Vehicle Entry</button>
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

    <hr>

    <h2>Parking History</h2>

    <p class="subtitle">
        View all registered vehicles and their entry and exit times.
    </p>

    <form method="GET" action="{{ url_for('home') }}">
        <label for="search">Search by vehicle number (optional)</label>
        <input
            id="search"
            name="search"
            value="{{ search }}"
            placeholder="Enter a vehicle number"
            maxlength="20"
        >
        <button type="submit">View Records</button>
        <a class="button-link" href="{{ url_for('home') }}">
            Show All Records
        </a>
    </form>

    {% if records %}
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Vehicle Number</th>
                        <th>Vehicle Type</th>
                        <th>Entry Time</th>
                        <th>Exit Time</th>
                        <th>Status</th>
                    </tr>
                </thead>

                <tbody>
                    {% for record in records %}
                    <tr>
                        <td>{{ record["id"] }}</td>
                        <td>{{ record["vehicle_number"] }}</td>
                        <td>{{ record["vehicle_type"] }}</td>
                        <td>{{ record["entry_time"] }}</td>
                        <td>{{ record["exit_time"] or "Not exited" }}</td>
                        <td>
                            {% if record["exit_time"] %}
                                <span class="status exited">Exited</span>
                            {% else %}
                                <span class="status active">Parked</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p class="empty">No parking records found.</p>
    {% endif %}

</main>
</body>
</html>
"""


def render_page(message=None, error=None, status=200):
    search = request.args.get("search", "").strip().upper()

    with db_connection() as conn:
        if search:
            records = conn.execute(
                """
                SELECT id, vehicle_number, vehicle_type,
                       entry_time, exit_time
                FROM vehicles
                WHERE vehicle_number LIKE ?
                ORDER BY id DESC
                """,
                (f"%{search}%",),
            ).fetchall()
        else:
            records = conn.execute(
                """
                SELECT id, vehicle_number, vehicle_type,
                       entry_time, exit_time
                FROM vehicles
                ORDER BY id DESC
                """
            ).fetchall()

    return (
        render_template_string(
            PAGE,
            message=message,
            error=error,
            records=records,
            search=search,
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
