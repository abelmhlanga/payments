from datetime import datetime, timedelta
from collections import defaultdict
import csv


class Payment:
    def __init__(self, payment_type, payment_amount, created_at, device_id):
        self.payment_type = payment_type
        self.payment_amount = payment_amount
        # self.created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        self.created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        self.device_id = device_id


def calculate_days_from_suspension(payment_history):
    """
    Calculates the days from suspension for a given device based on payment history.

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


def process_payments(payments_file="2024_09_10_payments.csv"):
    """
    Processes the payments CSV file and returns a dictionary of device IDs to payment history.

    Args:
        payments_file: The path to the payments CSV file.

    Returns:
        A dictionary of device IDs to lists of Payment objects.
    """
    
    payment_history = defaultdict(list)
    with open(payments_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            payment = Payment(
                row["payment_type"],
                float(row["payment_amount"]),
                row["created"],
                row["agent_user_id"],
                row["device_id"],
            )
            payment_history[payment.device_id].append(payment)
    return payment_history


def generate_reports(payment_history, output_dir):
    """
    Generates the three reports: days from suspension, agent collection, and payment type collection.

    Args:
        payment_history: A dictionary of device IDs to lists of Payment objects.
        output_dir: The directory to save the reports.
    """

    days_from_suspension_report = []
    agent_collection_report = defaultdict(lambda: defaultdict(int))
    payment_type_report = defaultdict(int)

    for device_id, payments in payment_history.items():
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
    payment_type_report = dict(sorted(payment_type_report.items()))

    # Generate report files
    with open(f"{output_dir}/days_from_suspension_report.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["device_id", "days_from_suspension"])
        writer.writerows(days_from_suspension_report)

    with open(f"{output_dir}/agent_collection_report.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["agent_user_id", "date", "payment_type", "total_amount"])