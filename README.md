# Database Backup Script

This Python script automatically backs up database files (.sql and .sqlite3) at midnight daily and sends email notifications about the backup status.

## Features

- Automatic backup of all .sql and .sqlite3 files at midnight (00:00 AM)
- Email notifications for successful or failed backups
- Configurable source and backup directories
- Organized backup structure with timestamps
- Detailed logging

## Requirements

- Python 3.6+
- Required packages (see requirements.txt)

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Configure the environment variables by copying the example file:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your email and backup settings:
   - `SENDER_EMAIL`: The email address used to send notifications
   - `APP_PASSWORD`: The app password for your email account (not your regular password)
   - `RECEIVER_EMAIL`: The email address to receive notifications
   - `SOURCE_DIR`: The directory containing database files to back up
   - `BACKUP_DIR`: The directory where backups will be stored

## Email Configuration

For Gmail, you'll need to use an app password:
1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification > App passwords
3. Create a new app password and use it in the .env file

## Usage

Run the script:
```
python db_backup.py
```

The script will:
1. Perform an initial backup immediately
2. Schedule future backups to run at midnight every day
3. Send status reports via email

To run the script in the background or as a service, you may want to use tools like:
- Windows: Task Scheduler
- Linux: systemd service or cron job

## Logs

The script creates a `backup.log` file in the same directory, containing detailed information about backup operations.
