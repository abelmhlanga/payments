import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from payments_processing import (
    Payment,
    calculate_days_from_suspension,
    process_payments,
    generate_reports,
)

class TestPayment(unittest.TestCase):
    def test_init(self):
        payment = Payment("CASH", 100, "2024-12-13 10:30:00", "12345")
        self.assertEqual(payment.payment_type, "CASH")
        self.assertEqual(payment.payment_amount, 100)
        self.assertEqual(payment.created_at, datetime(2024, 12, 13, 10, 30))
        self.assertEqual(payment.device_id, "12345")

class TestCalculateDaysFromSuspension(unittest.TestCase):
    @patch("datetime.datetime")
    def test_up_to_date(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 12, 15)
        payment_history = [
            Payment("CASH", 100, "2024-11-24 10:30:00", "12345")
        ]
        self.assertEqual(calculate_days_from_suspension(payment_history), 90)

    @patch("datetime.datetime")
    def test_grace_period_1(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 12, 13)
        payment_history = [
            Payment("CASH", 100, "2024-11-03 10:30:00", "12345")
        ]
        self.assertEqual(calculate_days_from_suspension(payment_history), 75)

    @patch("datetime.datetime")
    def test_grace_period_2(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 12, 15)
        payment_history = [
            Payment("CASH", 100, "2024-10-25 10:30:00", "12345")
        ]
        self.assertEqual(calculate_days_from_suspension(payment_history), 66)

    @patch("datetime.datetime")
    def test_suspended(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 9, 15)
        payment_history = [
            Payment("CASH", 100, "2024-09-15 10:30:00", "12345")
        ]
        self.assertEqual(calculate_days_from_suspension(payment_history), 0)

class TestProcessPayments(unittest.TestCase):
    def test_process_payments(self):
        with open("./2024_09_10_payments.csv", "r") as csvfile:
            payment_history = process_payments(csvfile)
        self.assertIsInstance(payment_history, dict)
        self.assertIn("12345", payment_history)
        self.assertIsInstance(payment_history["12345"], list)
        self.assertIsInstance(payment_history["12345"][0], Payment)

# We can add more tests for generate_reports function to cover different scenarios 

if __name__ == "__main__":
    unittest.main()