import csv
import pandas as pd
from datetime import datetime
import unittest
from unittest.mock import patch

from paymentsapp.payment_processing import Payment, calculate_days_from_suspension, generate_reports, process_payments

class TestPaymentProcessing(unittest.TestCase):
    @patch("datetime.datetime")
    def test_calculate_days_from_suspension(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2024, 12, 13)  # Current date for testing

        # Test case 1: Up to date on payments
        payment_history_1 = [
            Payment("CASH", 100, "2024-11-14 10:30:00", "12345")
        ]
        self.assertEqual(
            calculate_days_from_suspension(payment_history_1), 90
        )

        # Test case 2: Grace period 1
        payment_history_2 = [
            Payment("CASH", 100, "2024-11-03 10:30:00", "12345")
        ]
        self.assertEqual(
            calculate_days_from_suspension(payment_history_2), 70
        )

        # Test case 3: Grace period 2
        payment_history_3 = [
            Payment("CASH", 100, "2024-10-25 10:30:00", "12345")
        ]
        self.assertEqual(
            calculate_days_from_suspension(payment_history_3), 50
        )

        # Test case 4: Suspended
        payment_history_4 = [
            Payment("CASH", 100, "2024-09-15 10:30:00", "12345")
        ]
        self.assertEqual(
            calculate_days_from_suspension(payment_history_4), 0
        )

    def test_process_payments(self):
        # Create a sample in-memory DataFrame
        df = pd.DataFrame(
            [
                {
                    "payment_type": "CASH",
                    "payment_amount": 100,
                    "created": "2024-11-15 10:30:00",
                    "device_id": "12345",
                },
                {
                    "payment_type": "CARD",
                    "payment_amount": 50,
                    "created": "2024-11-10 14:00:00",
                    "device_id": "56789",
                },
            ]
        )

        # Iterate over chunks (in this case, just one chunk)
        payment_history_generator = process_payments(df, chunksize=2)
        first_chunk = next(payment_history_generator)

        self.assertIn("12345", first_chunk)
        self.assertIn("56789", first_chunk)
        self.assertIsInstance(first_chunk["12345"][0], Payment)
        self.assertEqual(first_chunk["12345"][0].payment_type, "CASH")

    def test_generate_reports_empty_history(self):
        empty_generator = iter([])  # Create an empty generator
        days, agent_collections, payment_types = generate_reports(
            empty_generator, "output_dir"
        )
        self.assertEqual(days, [])
        self.assertEqual(agent_collections, {})
        self.assertEqual(payment_types, {})

    def test_generate_reports_single_payment(self):
        payment_history_generator = iter(
            [
                {
                    "12345": [
                        Payment("CASH", 100, "2024-11-15 10:30:00", "12345")
                    ]
                }
            ]
        )
        days, agent_collections, payment_types = generate_reports(
            payment_history_generator, "output_dir"
        )
        self.assertEqual(len(days), 1)
        self.assertEqual(
            agent_collections,
            {
                "2024-11-15": {"CASH": 100.0}
            },
        )
        self.assertEqual(payment_types, {"CASH": 100.0})
