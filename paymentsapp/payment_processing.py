from datetime import datetime, timedelta
from collections import defaultdict, Counter
import csv
import unittest
from unittest.mock import patch
import pandas as pd


class Payment:
    def __init__(self, payment_type, payment_amount, created_at, device_id):
        self.payment_type = payment_type
        self.payment_amount = payment_amount
        self.created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        self.device_id = device_id


def calculate_days_from_suspension(payment_history):
    """
    Calculates days from suspension for a given device based on the payment history data.

    Args:
        payment_history: A list of Payment objects.

    Returns:
        The number of days from suspension for the device.
    """

    last_payment_date = max(payment.created_at for payment in payment_history)
    days_since_last_payment = (datetime.today() - last_payment_date).days

    if days_since_last_payment <= 30:
        return 90  # Up to date on payments
    elif days_since_last_payment <= 60:
        return 90 - (days_since_last_payment - 30)  # Grace period 1
    elif days_since_last_payment <= 91:
        return 90 - (days_since_last_payment - 60)  # Grace period 2
    else:
        return 0  # Suspended


def process_payments(payments_file, chunksize=10000):
    """
    Processes the payments CSV file in chunks using pandas and returns a generator 
    of dictionaries of device IDs to lists of Payment objects.

    Args:
        payments_file: The path to the payments CSV file.
        chunksize: Number of rows to read at a time.

    Yields:
        A dictionary of device IDs to lists of Payment objects for each chunk.
    """

    for chunk in pd.read_csv(payments_file, chunksize=chunksize):
        chunk_payment_history = defaultdict(list)
        for _, row in chunk.iterrows():
            payment = Payment(
                row["payment_type"],
                float(row["payment_amount"]),
                pd.to_datetime(row["created"]),  # Convert to pandas datetime
                row["device_id"],
            )
            chunk_payment_history[payment.device_id].append(payment)
        yield chunk_payment_history


def generate_reports(payment_history_generator, output_dir):
    """
    Generates the three reports: days from suspension, agent collection, and payment type collection.

    Args:
        payment_history_generator: A generator that yields dictionaries of device IDs to lists of Payment objects (from process_payments).
        output_dir: The directory to save the reports.
    """

    days_from_suspension_report = []
    agent_collection_report = defaultdict(lambda: defaultdict(int))
    payment_type_report = Counter()

    for chunk_payment_history in payment_history_generator:
        for device_id, payments in chunk_payment_history.items():
            days_from_suspension = calculate_days_from_suspension(payments)
            days_from_suspension_report.append((device_id, days_from_suspension))

            for payment in payments:
                agent_collection_report[payment.created_at.strftime("%Y-%m-%d")][
                    payment.payment_type
                ] += payment.payment_amount
                payment_type_report[payment.payment_type] += payment.payment_amount

    # Sort reports
    days_from_suspension_report.sort(key=lambda x: x[1], reverse=True)
    agent_collection_report = dict(sorted(agent_collection_report.items()))
    for agent, daily_collections in agent_collection_report.items():
        agent_collection_report[agent] = dict(sorted(daily_collections.items()))
    payment_type_report = dict(payment_type_report)  # Convert Counter to dict

    # Generate report files

    return (
        days_from_suspension_report,
        agent_collection_report,
        payment_type_report,
    )