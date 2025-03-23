from kafka import KafkaProducer
from datetime import datetime
import random
import re
from faker import Faker
from time import sleep
import json
from datetime import datetime, timezone



class BankFraudSimulation:

    def __init__(self, num_customers, fraud_chance):
        self.num_customers = num_customers
        self.fraud_chance = fraud_chance
        self.fake = Faker()
        self.customers = {}
        self.producer = KafkaProducer(
                        bootstrap_servers="localhost:9092",
                        value_serializer=lambda v: json.dumps(v).encode("utf-8")
                        )
        self.diff_login_devices = [
            "Smartphone (Mobile Banking App)", "Tablet (Mobile Banking App)", "Laptop (Web Browser)",
            "Desktop Computer (Web Browser)", "ATM (Card and PIN or Mobile App Login)",
            "Bank Kiosk (Self-service kiosk)", "Smartwatch (Mobile Banking App)", "Smart TV (Banking App)",
            "Voice Assistants (e.g., Amazon Alexa, Google Assistant for balance or transaction queries)",
            "POS Terminal (For card transactions and verification)", "Mobile Banking via SMS (SMS banking for transaction inquiries)",
            "Banking on a Public Computer (e.g., in a library or internet cafe)", "Banking through IoT Devices (e.g., smart home assistants for simple banking queries)",
            "Biometric Devices (Fingerprint or Face Recognition on mobile or desktop apps)",
            "Virtual Banking Assistants (Chatbots or Virtual Assistants for account management)",
            "Wearable Devices (Smartwatches for transaction notifications)"
        ]

        self.diff_card_types = ['Visa', 'MasterCard', 'American Express', 'Discover', 'Diners Club', 'JCB',
                               'UnionPay', 'Maestro', 'RuPay', 'Interac', 'Elo', 'Carte Bancaire', 'BC Card']

        self.diff_trans_types = ['Purchase', 'Refund', 'Withdrawal', 'Deposit', 'Transfer', 'Payment', 'Chargeback',
                                'Pre-authorization', 'Authorization', 'Capture', 'Void', 'Reversal', 'Balance Inquiry',
                                'Bill Payment', 'Fund Transfer', 'P2P Transfer', 'ATM Withdrawal', 'Merchant Payment',
                                'Recurring Payment', 'Direct Debit', 'Wire Transfer']
        
        self.generate_customers()

    def extract_city(self, address):
        """Extracts city from a fake address."""
        lines = address.split("\n")
        if len(lines) > 1:
            city_state_zip = lines[-1].split(",")
            return city_state_zip[0] if city_state_zip else "Unknown City"
        return "Unknown City"

    def extract_state(self, address):
        """Extracts state abbreviation from a fake address."""
        match = re.search(r",\s([A-Z]{2})\s\d{5}", address)
        return match.group(1) if match else "Unknown State"

    def generate_customer(self):
        """Generates a customer profile with random data."""
        name = self.fake.name()
        address = self.fake.address()
        email = f"{name.split()[0]}.{name.split()[1]}@gmail.com" if len(name.split()) > 1 else f"{name.split()[0]}@gmail.com"
        city = self.extract_city(address)
        state = self.extract_state(address)
        country = "US"
        ph_no = self.fake.phone_number()
        acc_no = f"ACC{random.randint(1000000000, 9999999999)}"
        ip_add = self.fake.ipv4()
        login_devices = random.sample(self.diff_login_devices, k=5)
        card_types = random.sample(self.diff_card_types, k=3)
        trans_types = random.sample(self.diff_trans_types, k=5)
        card_no = self.fake.credit_card_number()
        usual_mean_trans = random.randint(100, 5000)

        return {
            "Name": name, "Address": address, "Email": email, "City": city, "State": state, "Country": country,
            "Phone Number": ph_no, "Account Number": acc_no, "IP Address": ip_add, "Login Devices": login_devices,
            "Card Types": card_types, "Transaction Types": trans_types, "Card Number": card_no,
            "Usual Transaction Amount": usual_mean_trans
        }

    def generate_customers(self):
        """Creates multiple customers and stores them in a dictionary."""
        for i in range(self.num_customers):
            self.customers[str(i+1)] = self.generate_customer()

    def simulate_transaction(self, customer):
        """Simulates a transaction for a given customer."""
        transaction_id = f"TRN{random.randint(10000000000, 99999999999)}"
        transaction_time = str(datetime.now())

        is_fraudulent = random.randint(1, 100) <= self.fraud_chance
        multiplier = 12 if is_fraudulent else 1
        transaction_amount = random.uniform(customer["Usual Transaction Amount"] * 0.5,
                                            customer["Usual Transaction Amount"] * 1.5) * multiplier

        current_login_device = random.choice(customer["Login Devices"])
        current_card_type = random.choice(customer["Card Types"])
        current_transaction_type = random.choice(customer["Transaction Types"])

        transaction_data = {
            **customer,  # Merging customer data
            "Transaction ID": transaction_id, "Transaction Time": transaction_time,
            "Current Login Device": current_login_device, "Current Card Type": current_card_type,
            "Current Transaction Type": current_transaction_type, "Current Transaction Amount": transaction_amount
        }

        return transaction_data

    def check_fraud_flags(self, transaction_data):
        """Checks fraud flags based on transaction data."""
        fraud_flags = []

        if random.randint(1, 100) <= self.fraud_chance:
            fake_temp = Faker(random.choice([
                "en_US", "en_GB", "en_CA", "en_AU", "en_IN", "de_DE", "fr_FR", "es_ES", "it_IT",
                "nl_NL", "zh_CN", "ja_JP", "pt_BR", "ru_RU", "ko_KR"
            ]))
            country = fake_temp.country()
            if country != transaction_data["Country"]:
                fraud_flags.append(f"Different Country: {country}")

        if random.randint(1, 100) <= self.fraud_chance:
            ip_add = self.fake.ipv4()
            if ip_add != transaction_data["IP Address"]:
                fraud_flags.append(f"Different IP Address: {ip_add}")

        if random.randint(1, 100) <= self.fraud_chance:
            login_device = random.choice(self.diff_login_devices)
            if login_device != transaction_data["Current Login Device"]:
                fraud_flags.append(f"Different Login Device: {login_device}")

        if random.randint(1, 100) <= self.fraud_chance:
            trans_type = random.choice(self.diff_trans_types)
            if trans_type != transaction_data["Current Transaction Type"]:
                fraud_flags.append(f"Different Transaction Type: {trans_type}")

        if transaction_data["Current Transaction Amount"] > transaction_data["Usual Transaction Amount"] * 10:
            fraud_flags.append(f"Unusual Transaction Amount: {transaction_data['Current Transaction Amount']:.2f}")

        if fraud_flags:
            return {**transaction_data, "Fraud Flags": fraud_flags[0]}
        else:
            return {**transaction_data, "Fraud Flags": "No Fraud"}

    def run_simulation(self):
        """Runs fraud detection simulation on multiple customers."""
        print(f"Running simulation for {self.num_customers} customers with {self.fraud_chance}% fraud chance...\n")

        while True:
            select_customer = str(random.randint(1, self.num_customers))
            customer_data = self.customers[select_customer]

            # Simulate transaction
            transaction_data = self.simulate_transaction(customer_data)

            # Run fraud check
            fraud_checked_data = self.check_fraud_flags(transaction_data)

            # Kafka producer
            self.producer.send("bank_transactions", fraud_checked_data)
            # Print transaction data
            # print(fraud_checked_data)
            sleep(0.1)

# Example Usage:
num_customers = 10000  # Adjust as needed
fraud_chance = 5  # 5% fraud probability

bank_fraud_sim = BankFraudSimulation(num_customers, fraud_chance)
bank_fraud_sim.run_simulation()

