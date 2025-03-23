from kafka import KafkaConsumer
from email.message import EmailMessage
import smtplib
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Connect to Kafka topic
consumer = KafkaConsumer(
    "blocked_customers",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    group_id="email_alerts_group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

print("📬 Email Alert Engine listening for blocked customers...")

# Define threshold
THRESHOLD = 10000

for msg in consumer:
    data = msg.value
    amount = data.get("Current Transaction Amount", 0)
    reason = data.get("Reason", "")
    
    if amount > THRESHOLD or "Fraud" in reason:
        # Compose email
        email = EmailMessage()
        email["From"] = EMAIL_FROM
        email["To"] = EMAIL_TO
        email["Subject"] = f"🚨 Blocked Customer Alert: {data.get('Name', 'Unknown')}"
        
        body = f"""
        A customer has been blocked!

        Name: {data.get('Name')}
        Account Number: {data.get('Account Number')}
        Transaction ID: {data.get('Transaction ID')}
        Amount: ${amount:,.2f}
        Reason: {reason}
        Time: {data.get('Transaction Time')}
        """
        email.set_content(body)

        # Send email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(email)
                print(f"✅ Email alert sent for {data.get('Name')}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
