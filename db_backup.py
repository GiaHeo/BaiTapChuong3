import os
import time
import shutil
import smtplib
import logging
import schedule
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='backup.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Email configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# Backup configuration
SOURCE_DIR = os.getenv('SOURCE_DIR', os.getcwd())  # Default to current directory if not specified
BACKUP_DIR = os.getenv('BACKUP_DIR', os.path.join(os.getcwd(), 'backup'))  # Default backup folder


def send_email(subject, message):
    """Send an email with the given subject and message."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to server and send
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            
        logger.info("Email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def backup_databases():
    """Backup all .sql and .sqlite3 files in the source directory to the backup directory."""
    try:
        # Create timestamp for the backup folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_folder, exist_ok=True)
        
        # Find all database files
        source_path = Path(SOURCE_DIR)
        db_files = list(source_path.glob('**/*.sql')) + list(source_path.glob('**/*.sqlite3'))
        
        if not db_files:
            message = f"No database files found in {SOURCE_DIR}"
            logger.warning(message)
            send_email("Database Backup Warning", message)
            return
        
        # Copy each file to the backup folder
        successful_backups = []
        failed_backups = []
        
        for file in db_files:
            try:
                # Create relative path structure in the backup folder
                rel_path = file.relative_to(source_path)
                backup_file = os.path.join(backup_folder, str(rel_path))
                
                # Create directory structure if needed
                os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                
                # Copy the file
                shutil.copy2(file, backup_file)
                successful_backups.append(str(file))
                logger.info(f"Successfully backed up {file}")
            except Exception as e:
                failed_backups.append(f"{file}: {str(e)}")
                logger.error(f"Failed to backup {file}: {str(e)}")
        
        # Prepare email message
        subject = "Database Backup Report"
        message = f"Database Backup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if successful_backups:
            message += "Successfully backed up the following files:\n"
            message += "\n".join(successful_backups)
            message += "\n\n"
        
        if failed_backups:
            message += "Failed to backup the following files:\n"
            message += "\n".join(failed_backups)
            subject = "Database Backup Error Report"
        else:
            message += f"All database files were successfully backed up to: {backup_folder}"
        
        # Send email report
        send_email(subject, message)
        
    except Exception as e:
        error_message = f"Backup process failed: {str(e)}"
        logger.error(error_message)
        send_email("Database Backup Critical Error", error_message)


def main():
    """Main function to set up the schedule and run the program."""
    logger.info("Database backup service started")
    
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Schedule the backup task to run at midnight (00:00) every day
    schedule.every().day.at("00:00").do(backup_databases)
    
    # Also run a backup immediately when the script starts
    logger.info("Running initial backup...")
    backup_databases()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
