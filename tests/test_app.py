
import os
import tempfile
import unittest

import app as parking_app


class ParkingManagementTests(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

        self.original_database = parking_app.DATABASE
        parking_app.DATABASE = self.temp_file.name
        parking_app.init_db()

        parking_app.app.config["TESTING"] = True
        self.client = parking_app.app.test_client()

    def tearDown(self):
        parking_app.DATABASE = self.original_database

        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def add_vehicle(self, number="TN01AB1234", vehicle_type="Car"):
        return self.client.post(
            "/add",
            data={
                "vehicle_number": number,
                "vehicle_type": vehicle_type,
            },
        )

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parking Management System", response.data)

    def test_add_vehicle(self):
        response = self.add_vehicle()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Vehicle entry recorded successfully!",
            response.data,
        )

    def test_invalid_vehicle_type(self):
        response = self.add_vehicle(vehicle_type="Helicopter")
        self.assertEqual(response.status_code, 400)

    def test_exit_vehicle(self):
        self.add_vehicle()

        response = self.client.post(
            "/exit",
            data={"vehicle_number": "TN01AB1234"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Vehicle exit recorded successfully!",
            response.data,
        )

    def test_exit_vehicle_without_active_entry(self):
        response = self.client.post(
            "/exit",
            data={"vehicle_number": "TN99ZZ9999"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            b"No active parking entry found",
            response.data,
        )


if __name__ == "__main__":
    unittest.main()
