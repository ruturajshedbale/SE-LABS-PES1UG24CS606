"""Regression tests for the car rental static-analysis lab."""

import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

import car_rental


class CarRentalTests(unittest.TestCase):
    """Cover input validation and the security fixes in the demo."""

    def setUp(self) -> None:
        car_rental.FLEET.clear()
        car_rental.BOOKINGS.clear()
        car_rental.DATABASE_CONNECTION.execute("DELETE FROM customers")
        car_rental.add_car("KA01AB1234", "Swift", 1500)
        car_rental.register_customer("Ravi", "DL-12345", "5550100")

    def test_customer_lookup_treats_sql_as_data(self) -> None:
        self.assertEqual(car_rental.find_customer("Ravi")[0][0], "Ravi")
        self.assertEqual(car_rental.find_customer("x' OR '1'='1"), [])

    def test_rental_validates_dates_and_availability(self) -> None:
        self.assertEqual(
            car_rental.rent_car(
                "KA01AB1234", "Ravi", "2026-11-01", "2026-11-04"
            ),
            4500,
        )
        with self.assertRaises(ValueError):
            car_rental.rent_car(
                "KA01AB1234", "Ravi", "2026-11-05", "2026-11-06"
            )
        with self.assertRaises(ValueError):
            car_rental.rent_car(
                "KA01AB1234", "Ravi", "2026-11-04", "2026-11-01"
            )
        self.assertEqual(car_rental.return_car("KA01AB1234", 420), 600)
        self.assertIn("KA01AB1234", car_rental.available_cars())

    def test_invalid_rate_and_unknown_car_are_reported(self) -> None:
        with self.assertRaises(ValueError):
            car_rental.add_car("KA02CD5678", "Innova", -1)
        with self.assertRaises(KeyError):
            car_rental.return_car("XX00XX0000", 10)

    def test_default_features_are_independent(self) -> None:
        first = car_rental.add_car("KA02CD5678", "Innova", 3000)
        second = car_rental.add_car("KA03EF9999", "Nexon", 2000)
        first["features"].append("GPS")
        self.assertEqual(second["features"], [])

    def test_promo_parser_rejects_executable_input(self) -> None:
        self.assertEqual(
            car_rental.apply_promo("amount = amount * 0.9", 4500),
            4050,
        )
        with self.assertRaises(ValueError):
            car_rental.apply_promo("__import__('os').system('whoami')", 4500)

    def test_licence_digest_uses_a_unique_salt(self) -> None:
        first = car_rental.licence_hash("DL-12345")
        second = car_rental.licence_hash("DL-12345")
        self.assertNotEqual(first, second)
        self.assertEqual(len(first.split(":")), 2)

    def test_booking_codes_and_plate_validation(self) -> None:
        self.assertRegex(
            car_rental.booking_code(),
            re.compile(r"^BK-[A-F0-9]{8}$"),
        )
        self.assertTrue(car_rental.is_valid_plate("KA01AB1234"))
        self.assertFalse(car_rental.is_valid_plate("not-a-plate"))

    def test_admin_login_requires_configured_password(self) -> None:
        test_password = {"CAR_RENTAL_ADMIN_PASSWORD": "safe-test"}
        with patch.dict(os.environ, test_password):
            self.assertTrue(car_rental.admin_login("admin", "safe-test"))
            self.assertFalse(car_rental.admin_login("admin", "wrong"))
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(car_rental.admin_login("admin", "safe-test"))

    def test_receipt_is_written_with_utf8_text(self) -> None:
        booking = {
            "code": "BK-TEST",
            "plate": "KA01AB1234",
            "days": 3,
            "cost": 4500,
        }
        receipt = Path(car_rental.write_receipt(booking))
        self.addCleanup(receipt.unlink, missing_ok=True)
        self.assertIn("BK-TEST", receipt.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
