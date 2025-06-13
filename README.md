# work-anniversary-email-automation
Developed for CBT


# Work Anniversary Email Automation

This project automates the detection of employee work anniversaries from a Google Sheet and sends personalized reminder or celebration emails based on the date.

## 🔧 Features

- Reads employee data from a Google Sheet (e.g., "In" date, Name, Email, Status).
- Parses multiple date formats (e.g., `dd/mmm/yy`, `dd/mm/yyyy`).
- Sends:
  - 🎉 Celebration emails on the anniversary day.
  - ⏰ Reminder emails 7 days before.
- Distinguishes between:
  - Recruiters → Email sent directly to them with team in CC.
  - Staff (non-recruiters) → Email sent to team with manager in CC.
- Uses `smtplib` to send emails via Gmail SMTP.
- Retries Google Sheet loading on transient errors.

## 🧪 Screenshot

![image](https://github.com/user-attachments/assets/f882108f-821e-446d-b42a-bfa23e69bb4d)


## 🛠️ Tech Stack

- **Python** (datetime, pandas, smtplib)
- **Google Sheets API** (`gspread`, `google-auth`)
- **Gmail SMTP** (for sending emails)

## 📁 Project Structure

```bash
├── anniversary_reminder.py   # Main script
├── credentials.json          # Google Sheets service account key
├── README.md

🔒 Security Notes
Store your Gmail app password securely (use .env or secret managers).

Never push credentials.json to GitHub.

🚀 How to Run
Replace placeholders like:

your.email@example.com

your_app_password_here

https://docs.google.com/spreadsheets/d/your_sheet_id_here/

Install dependencies:

pip install pandas gspread google-auth

python anniversary_reminder.py
📅 Sample Use Case
Perfect for HR and Data teams who want to automatically recognize team members' anniversaries without manual tracking or reminders.


