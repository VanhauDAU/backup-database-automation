import os
import shutil
import smtplib
import schedule
import time
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'database_main')
BACKUP_DIR = os.path.join(BASE_DIR, 'backup')

# Kiểm tra và tạo thư mục nếu không tồn tại
if not os.path.exists(DATABASE_DIR):
    print(f"Thư mục '{DATABASE_DIR}' không tồn tại. Vui lòng kiểm tra lại!")
    exit()

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
    print(f"Thư mục '{BACKUP_DIR}' đã được tạo.")

# thông tin mail
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
# hàm gửi mail
def send_email(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Gửi mail thành công!.")
    except Exception as e:
        print("Gửi mail thất bại:", e)
# hàm backup dữ liệu
def backup_database():
    try:
        files_backed_up = []
        for filename in os.listdir(DATABASE_DIR):
            if filename.endswith('.sql') or filename.endswith('.sqlite3'):
                source = os.path.join(DATABASE_DIR, filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest_filename = f"{filename.replace('.', f'_{timestamp}.')}"
                dest = os.path.join(BACKUP_DIR, dest_filename)
                shutil.copy2(source, dest)
                files_backed_up.append(dest_filename)

        if files_backed_up:
            send_email("Backup dữ liệu Thành Công", "\n".join(files_backed_up))
        else:
            send_email("Không tìm thấy file database", "Không có file .sql hoặc .sqlite3 nào để backup.")
    except Exception as e:
        send_email("Backup thất bại", str(e))

schedule.every().day.at("00:00").do(backup_database)  

print("Chương trình đang chạy và sẽ tự động backup lúc 00:00 mỗi ngày...")

# Vòng lặp chạy kiểm tra thời gian
while True:
    schedule.run_pending()
    time.sleep(1)
