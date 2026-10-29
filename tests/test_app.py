import os
import tempfile
import unittest

import app as parking_app


class ParkingManagementTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database = parking_app.DATABASE
        parking_app.DATABASE = os.path.join(
            self.temp_dir.name, "test_parking.db"
        )
        parking_app.app.config["TESTING"] = True
        parking_app.init_db()
        self.client = parking_app.app.test_client()

    def tearDown(self):
        parking_app.DATABASE = self.original_database
        self.temp_dir.cleanup()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parking Management System", response.data)

    def test_add_vehicle(self):
        response = self.client.post(
            "/add",
            data={
                "vehicle_number": "TN01AB1234",
                "vehicle_type": "Car",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Vehicle entry recorded successfully",
            response.data,
        )

    def test_exit_vehicle(self):
        self.client.post(
            "/add",
            data={
                "vehicle_number": "TN01AB1234",
                "vehicle_type": "Car",
            },
        )
        response = self.client.post(
            "/exit",
            data={"vehicle_number": "TN01AB1234"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Vehicle exit recorded successfully",
            response.data,
        )

    def test_exit_unknown_vehicle(self):
        response = self.client.post(
            "/exit",
            data={"vehicle_number": "UNKNOWN123"},
        )
        self.assertEqual(response.status_code, 404)

    def test_search_vehicle(self):
        self.client.post(
            "/add",
            data={
                "vehicle_number": "TN01AB1234",
                "vehicle_type": "Car",
            },
        )
        response = self.client.get("/?search=TN01AB1234")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TN01AB1234", response.data)


if __name__ == "__main__":
    unittest.main()
