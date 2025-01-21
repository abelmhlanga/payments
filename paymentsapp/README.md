Lumkani Payment Processing Program - README.md

This document describes how to run the Lumkani Payment Processing program, which analyzes payment history data to generate reports on client statuses and agent collections. The program is designed for scalability and utilizes efficient data structures for improved performance.

Installation
The program is written in Python and requires no specific installation. However, you'll need Python 3.x installed on your system. You can verify your Python version by running python --version or python3 --version in your terminal.

Dependencies:
The program requires the following libraries:

pandas
collections
You can install them using pip:

Bash

pip install pandas collections
Running the Program
The program accepts three arguments:

Payments File: Path to the CSV file containing payment history data. The file format is:
id,payment_type,payment_amount,payment_signature_image,payment_photo,created,status,notes,agent_user_id,device_id
Ensure the date format in the created column is YYYY-MM-DD HH:MM:SS

Output Directory: Path to a directory where the program will generate the reports. This directory should not exist before running the program.
Chunk Size (Optional): (Default: 10000) Number of rows to process from the CSV file in each chunk. Use this option to adjust memory usage for large datasets.
Example Usage:

Bash


python payments_processing.py 2024_09_10_payments.csv reports --chunksize=20000

This command will run the program using the 2024_09_10_payments, generate reports in the reports directory, and process the data in chunks of 20,000 rows.


Generated Reports
The program generates three reports in the specified output directory:

days_from_suspension_report.csv: This report lists device IDs and the corresponding number of days remaining until suspension based on payment history.

agent_collection_report.csv: This report details daily collections categorized by agent, date, and payment type.

payment_type_report.csv: This report summarizes total collections for each unique payment type.

These reports are generated in CSV format and can be opened with any spreadsheet application.

Unit Tests
The program includes unit tests to ensure its functionality. You can run the tests using:

Bash

python -m unittest test_payment_processing.py

This will execute the unit tests and provide feedback on any potential issues.

Key Considerations for efficiency and Scalability:

Date Format Handling:
The Payment class constructor now uses %m/%d/%Y %H:%M as the date format string in datetime.strptime() to handle the date format in the provided CSV.

Column Selection:
The pd.read_csv() function now includes usecols to specify the columns needed for processing: "payment_type", "payment_amount", "created", and "device_id". 
This improves efficiency by reading only the required columns from the CSV file.

Using Counter for payment_type_report:

Replaced defaultdict(int) with Counter from the collections module.
Counter is specifically designed for efficiently counting hashable objects (like payment types in this case).
It provides optimized implementations for incrementing counts, making it more efficient than using a defaultdict(int).

Converting Counter to Dictionary:

After processing all payments, the payment_type_report (which is a Counter object) is converted to a regular dictionary using dict(payment_type_report). This is necessary for writing the report to the CSV file.
This revised code improves the efficiency of the generate_reports function by utilizing the optimized counting capabilities of the Counter class for the payment_type_report.

Abel Mhlanga.
Cape Town, South Africa.
Copyright (C) 2024, Abel  Mhlanga