# -*- coding: utf-8 -*-
"""
Automated Work Anniversary Reminder System

This script checks a Google Sheet for employees with upcoming or current work anniversaries
and sends email reminders or celebration messages accordingly.

Sensitive information like email addresses, names, and credentials have been anonymized.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time

# List of staff members who should be treated as non-recruiters
NON_RECRUITERS = [
    "John Doe", "Jane Smith", "Lucas White", "Maria Green",
    "Elena Black", "Omar Red", "Noah Blue", "Emma Grey"
]

# Recipients for non-recruiter messages
TO_ADDRESSES = [
    'recipient1@example.com',
    'recipient2@example.com'
]

# CC recipient for staff anniversaries
CC_EMAIL = 'manager@example.com'

# Authenticate Google Sheets access using service account
def authenticate_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    return gspread.authorize(creds)

# Load Google Sheet and return as DataFrame
def load_google_sheet(sheet_url, max_retries=3, backoff_factor=2):
    client = authenticate_google_sheets()
    for attempt in range(max_retries):
        try:
            sheet = client.open_by_url(sheet_url)
            data = sheet.get_worksheet(0).get_all_records()
            return pd.DataFrame(data)
        except gspread.exceptions.APIError as e:
            if "500" in str(e):  # Retry only on server errors
                wait_time = backoff_factor ** attempt
                print(f"APIError: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Failed to load Google Sheets after multiple retries.")

# Parse various date formats in the 'In' column
def parse_save_date(date):
    if pd.isna(date):
        return date
    for fmt in ("%d/%b/%y", "%d/%m/%Y"):
        try:
            return pd.to_datetime(date, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(date, errors='coerce')

# Send email using Gmail SMTP

def send_email(to_address, cc_addresses, subject, body):
    from_address = 'your.email@example.com'  # Replace with your email
    password = 'your_app_password_here'      # Replace with your app password

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address if isinstance(to_address, str) else ', '.join(to_address)
    msg['Cc'] = ', '.join(cc_addresses) if cc_addresses else ''
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()
        print(f'Email sent to {msg["To"]} with CC to {msg["Cc"]}')
    except Exception as e:
        print(f'Failed to send email: {e}')

# Main logic to detect anniversaries and send appropriate messages
def process_anniversaries(df):
    found_anniversary = False
    today = datetime.now().date()

    for _, row in df.iterrows():
        if row.get('Status') != 'Active':
            continue

        if pd.notna(row['In']):
            anniversary_date = row['In'].date()
            next_anniversary = anniversary_date.replace(year=today.year)

            if next_anniversary < today:
                next_anniversary = next_anniversary.replace(year=today.year + 1)

            years = today.year - anniversary_date.year
            if today < anniversary_date.replace(year=today.year):
                years -= 1

            if years < 1:
                continue

            # Anniversary Today
            if next_anniversary == today:
                found_anniversary = True
                if row['Name'] in NON_RECRUITERS:
                    subject = f"Today: Work Anniversary for {row['Name']}"
                    body = (
                        f"Dear Team,\n\n"
                        f"Today marks {row['Name']}'s {years}-year work anniversary.\n"
                        f"Let's recognize their valuable contributions.\n\n"
                        f"Best regards,\nData Team"
                    )
                    send_email(TO_ADDRESSES, [CC_EMAIL], subject, body)
                else:
                    subject = f"🎉 Happy Work Anniversary, {row['Name']}! 🎉"
                    body = (
                        f"Hi {row['Name']},\n\n"
                        f"Congratulations on your {years}-year work anniversary!\n"
                        f"Thank you for your hard work and dedication.\n\n"
                        f"Best,\nYour Team"
                    )
                    send_email(row['Email'], TO_ADDRESSES, subject, body)

            # Reminder 7 days in advance
            elif next_anniversary == (today + timedelta(days=7)):
                found_anniversary = True
                subject = f"Upcoming Work Anniversary for {row['Name']}"
                body = (
                    f"Dear Team,\n\nReminder: {row['Name']}'s {years + 1}-year work anniversary is on "
                    f"{next_anniversary.strftime('%d/%m/%Y')}.\n\nBest regards,\nData Team"
                )
                send_email(TO_ADDRESSES, [], subject, body)

    if not found_anniversary:
        print("No work anniversaries today or in 7 days.")

# Load the spreadsheet and process the anniversaries
sheet_url = 'https://docs.google.com/spreadsheets/d/your_sheet_id_here/'  # Replace with your sheet URL
df = load_google_sheet(sheet_url)
df['In'] = df['In'].apply(parse_save_date)
process_anniversaries(df)
