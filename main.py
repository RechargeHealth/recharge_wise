import sys
import json
import warnings
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                           QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt
import requests

# Suppress urllib3 warning
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

class WiseAPITester(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    # Add macOS secure coding support
    if sys.platform == 'darwin':
        def applicationSupportsSecureRestorableState_(self, *args, **kwargs):
            return True

    def initUI(self):
        layout = QVBoxLayout()

        # API Token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel('API Token:'))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)

        # Fetch Profile Button and Dropdown
        profile_section = QHBoxLayout()
        self.fetch_profile_button = QPushButton('Fetch Profiles')
        self.fetch_profile_button.clicked.connect(self.fetch_profiles)
        profile_section.addWidget(self.fetch_profile_button)
        
        profile_section.addWidget(QLabel('Profile ID:'))
        self.profile_dropdown = QComboBox()
        self.profile_dropdown.currentIndexChanged.connect(self.on_profile_changed)
        profile_section.addWidget(self.profile_dropdown)
        
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText('Or enter Profile ID manually')
        profile_section.addWidget(self.profile_input)
        layout.addLayout(profile_section)

        # Sandbox Checkbox and API Version Dropdown
        env_version_layout = QHBoxLayout()
        self.sandbox_checkbox = QCheckBox('Use Sandbox')
        self.sandbox_checkbox.setChecked(True)
        env_version_layout.addWidget(self.sandbox_checkbox)
        env_version_layout.addWidget(QLabel('API Version:'))
        self.version_dropdown = QComboBox()
        self.version_dropdown.addItems(['v1', 'v2', 'v3'])
        self.version_dropdown.setCurrentText('v3')
        env_version_layout.addWidget(self.version_dropdown)
        layout.addLayout(env_version_layout)

        # Fetch Balances Button
        self.fetch_balances_button = QPushButton('Fetch Balances')
        self.fetch_balances_button.clicked.connect(self.fetch_balances)
        layout.addWidget(self.fetch_balances_button)

        # Balance ID Dropdown
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel('Balance ID:'))
        self.balance_dropdown = QComboBox()
        balance_layout.addWidget(self.balance_dropdown)
        layout.addLayout(balance_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel('Currency:'))
        self.currency_input = QLineEdit()
        self.currency_input.setText('GBP')
        currency_layout.addWidget(self.currency_input)
        layout.addLayout(currency_layout)

        # Date Range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('Start Date:'))
        self.start_date_input = QLineEdit()
        self.start_date_input.setText('2023-08-01T00:00:00.000Z')
        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(QLabel('End Date:'))
        self.end_date_input = QLineEdit()
        self.end_date_input.setText('2024-08-31T23:59:59.999Z')
        date_layout.addWidget(self.end_date_input)
        layout.addLayout(date_layout)

        # Fetch Statement Button
        self.fetch_button = QPushButton('Fetch Statement')
        self.fetch_button.clicked.connect(self.fetch_statement)
        layout.addWidget(self.fetch_button)

        # Status Label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Tabs for displaying results
        self.tabs = QTabWidget()
        self.raw_result_display = QTextEdit()
        self.raw_result_display.setReadOnly(True)
        self.tabs.addTab(self.raw_result_display, "Raw JSON")

        # Create scrollable area for formatted display
        self.formatted_result_display = QScrollArea()
        self.formatted_result_display.setWidgetResizable(True)
        self.formatted_content = QWidget()
        self.formatted_layout = QVBoxLayout(self.formatted_content)
        self.formatted_result_display.setWidget(self.formatted_content)
        self.tabs.addTab(self.formatted_result_display, "Formatted Statement")

        layout.addWidget(self.tabs)

        self.setLayout(layout)
        self.setWindowTitle('Wise API Tester')
        self.setGeometry(300, 300, 1400, 800)

    def fetch_profiles(self):
        token = self.token_input.text()
        if not token:
            QMessageBox.warning(self, 'Input Error', 'Please enter API Token.')
            return

        use_sandbox = self.sandbox_checkbox.isChecked()
        base_url = "https://api.sandbox.transferwise.tech" if use_sandbox else "https://api.transferwise.com"
        url = f"{base_url}/v2/profiles"
        
        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            self.status_label.setText("Fetching profiles...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            profiles = response.json()
            
            self.profile_dropdown.clear()
            for profile in profiles:
                profile_type = profile.get('type', 'Unknown')
                profile_name = profile.get('businessName', profile.get('firstName', '')) + ' ' + profile.get('lastName', '')
                display_text = f"{profile['id']} ({profile_type} - {profile_name.strip()})"
                self.profile_dropdown.addItem(display_text, profile['id'])
            
            self.status_label.setText("Profiles fetched successfully!")
            self.raw_result_display.setPlainText(json.dumps(profiles, indent=2))
            
        except requests.exceptions.RequestException as e:
            error_message = f"API Error: {str(e)}\n\nURL: {url}\n\nResponse: {e.response.text if e.response else 'No response'}"
            QMessageBox.critical(self, 'API Error', error_message)
            self.status_label.setText("Failed to fetch profiles!")
            self.raw_result_display.setPlainText(error_message)

    def on_profile_changed(self, index):
        if index >= 0:
            profile_id = self.profile_dropdown.currentData()
            self.profile_input.setText(str(profile_id))

    def fetch_balances(self):
        token = self.token_input.text()
        profile_id = self.profile_input.text()
        use_sandbox = self.sandbox_checkbox.isChecked()

        if not all([token, profile_id]):
            QMessageBox.warning(self, 'Input Error', 'Please enter API Token and Profile ID.')
            return

        base_url = "https://api.sandbox.transferwise.tech" if use_sandbox else "https://api.transferwise.com"
        url = f"{base_url}/v1/borderless-accounts?profileId={profile_id}"
        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            self.status_label.setText("Fetching balances...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.balance_dropdown.clear()
            for account in data:
                for balance in account['balances']:
                    self.balance_dropdown.addItem(f"{balance['id']} ({balance['currency']})", balance['id'])
            
            self.status_label.setText("Balances fetched successfully!")
            QMessageBox.information(self, 'Success', 'Balances fetched successfully!')
            self.raw_result_display.setPlainText(json.dumps(data, indent=2))

        except requests.exceptions.RequestException as e:
            error_message = f"API Error: {str(e)}\n\nURL: {url}\n\nHeaders: {dict(e.response.headers) if e.response else 'No headers'}\n\nResponse: {e.response.text if e.response else 'No response'}"
            QMessageBox.critical(self, 'API Error', error_message)
            self.status_label.setText("Failed to fetch balances!")
            self.raw_result_display.setPlainText(error_message)

    def fetch_statement(self):
        token = self.token_input.text()
        profile_id = self.profile_input.text()
        balance_id = self.balance_dropdown.currentData()
        currency = self.currency_input.text()
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()
        use_sandbox = self.sandbox_checkbox.isChecked()
        api_version = self.version_dropdown.currentText()

        if not all([token, profile_id, balance_id, currency, start_date, end_date]):
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields and fetch balances.')
            return

        base_url = "https://api.sandbox.transferwise.tech" if use_sandbox else "https://api.transferwise.com"
        url = f"{base_url}/{api_version}/profiles/{profile_id}/balance-statements/{balance_id}/statement.json"
        params = {
            'currency': currency,
            'intervalStart': start_date,
            'intervalEnd': end_date
        }
        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            self.status_label.setText("Fetching statement...")
            response = requests.get(url, params=params, headers=headers)
            self.raw_result_display.setPlainText(f"Status Code: {response.status_code}\n\nHeaders: {dict(response.headers)}\n\nResponse:\n{response.text}")
            response.raise_for_status()
            data = response.json()
            self.raw_result_display.setPlainText(json.dumps(data, indent=2))
            self.display_formatted_statement(data)
            self.status_label.setText("Statement fetched successfully!")
        except requests.exceptions.RequestException as e:
            error_message = f"API Error: {str(e)}\n\nURL: {url}\n\nParams: {params}\n\nHeaders: {dict(e.response.headers) if e.response else 'No headers'}\n\nResponse: {e.response.text if e.response else 'No response'}"
            QMessageBox.critical(self, 'API Error', error_message)
            self.status_label.setText("Failed to fetch statement!")
            self.raw_result_display.setPlainText(error_message)

    def display_formatted_statement(self, data):
        try:
            # Clear previous content - modified clearing logic
            while self.formatted_layout.count():
                child = self.formatted_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Account Holder Info
            account_holder_label = QLabel(f"Account Holder: {data['accountHolder']['businessName']}")
            self.formatted_layout.addWidget(account_holder_label)

            # Balance Info
            balance_label = QLabel(f"Start Balance: {data['startOfStatementBalance']['value']} {data['startOfStatementBalance']['currency']}")
            self.formatted_layout.addWidget(balance_label)
            balance_label = QLabel(f"End Balance: {data['endOfStatementBalance']['value']} {data['endOfStatementBalance']['currency']}")
            self.formatted_layout.addWidget(balance_label)

            # Transactions Table
            transactions_table = QTableWidget()
            transactions_table.setColumnCount(11)
            transactions_table.setHorizontalHeaderLabels([
                "Date", "Type", "Amount", "Currency", "Description", 
                "Fees", "Transaction Details", "Exchange Rate", 
                "Running Balance", "Reference", "Recipient"
            ])
            transactions_table.setRowCount(len(data['transactions']))

            for row, transaction in enumerate(data['transactions']):
                # Format date to be more readable
                date_str = transaction['date']
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_date = date_str

                transactions_table.setItem(row, 0, QTableWidgetItem(formatted_date))
                transactions_table.setItem(row, 1, QTableWidgetItem(transaction['type']))
                transactions_table.setItem(row, 2, QTableWidgetItem(f"{transaction['amount']['value']:,.2f}"))
                transactions_table.setItem(row, 3, QTableWidgetItem(transaction['amount']['currency']))
                transactions_table.setItem(row, 4, QTableWidgetItem(transaction['details']['description']))
                
                # Fees
                fees = transaction['totalFees']['value'] if transaction['totalFees']['value'] != 0 else '-'
                transactions_table.setItem(row, 5, QTableWidgetItem(str(fees)))
                
                # Transaction Details
                if transaction['details']['type'] == 'CONVERSION':
                    details = f"From: {transaction['details']['sourceAmount']['value']:,.2f} {transaction['details']['sourceAmount']['currency']}\n"
                    details += f"To: {transaction['details']['targetAmount']['value']:,.2f} {transaction['details']['targetAmount']['currency']}"
                elif transaction['details']['type'] == 'DEPOSIT':
                    details = f"Sender: {transaction['details'].get('senderName', 'N/A')}\n"
                    details += f"Sender Account: {transaction['details'].get('senderAccount', 'N/A')}\n"
                    details += f"Payment Reference: {transaction['details'].get('paymentReference', 'N/A')}"
                else:
                    details = transaction['details']['type']
                transactions_table.setItem(row, 6, QTableWidgetItem(details))
                
                # Exchange Rate
                exchange_rate = '-'
                if transaction['exchangeDetails']:
                    exchange_rate = f"{transaction['exchangeDetails']['rate']:,.6f}"
                elif 'rate' in transaction['details']:
                    exchange_rate = f"{transaction['details']['rate']:,.6f}"
                transactions_table.setItem(row, 7, QTableWidgetItem(exchange_rate))
                
                # Running Balance
                running_balance = f"{transaction['runningBalance']['value']:,.2f} {transaction['runningBalance']['currency']}"
                transactions_table.setItem(row, 8, QTableWidgetItem(running_balance))

                # Reference Number
                transactions_table.setItem(row, 9, QTableWidgetItem(transaction['referenceNumber']))

                # Recipient
                recipient = transaction['details'].get('recipient', {})
                if recipient:
                    recipient_info = f"{recipient.get('name', 'N/A')}\n{recipient.get('bankAccount', 'N/A')}"
                elif transaction['details'].get('type') == 'DEPOSIT':
                    recipient_info = f"Sender: {transaction['details'].get('senderName', 'N/A')}"
                else:
                    recipient_info = '-'
                transactions_table.setItem(row, 10, QTableWidgetItem(recipient_info))

                # Color coding for transaction types
                for col in range(transactions_table.columnCount()):
                    item = transactions_table.item(row, col)
                    if item:
                        if transaction['type'] == 'CREDIT':
                            item.setBackground(Qt.darkGreen)
                            item.setForeground(Qt.white)
                        elif transaction['type'] == 'DEBIT':
                            item.setBackground(Qt.darkRed)
                            item.setForeground(Qt.white)

            # Set table properties
            transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            transactions_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
            transactions_table.setSelectionMode(QTableWidget.ContiguousSelection)
            transactions_table.setSortingEnabled(True)

            # Add the table to the layout
            self.formatted_layout.addWidget(transactions_table)

            # Add summary section
            summary_layout = QVBoxLayout()
            
            # Transaction counts
            total_transactions = len(data['transactions'])
            credit_transactions = sum(1 for t in data['transactions'] if t['type'] == 'CREDIT')
            debit_transactions = sum(1 for t in data['transactions'] if t['type'] == 'DEBIT')
            
            summary_label = QLabel(f"""
                Summary:
                Total Transactions: {total_transactions}
                Credit Transactions: {credit_transactions}
                Debit Transactions: {debit_transactions}
                
                Start Balance: {data['startOfStatementBalance']['value']:,.2f} {data['startOfStatementBalance']['currency']}
                End Balance: {data['endOfStatementBalance']['value']:,.2f} {data['endOfStatementBalance']['currency']}
                
                Period: {data['query']['intervalStart']} to {data['query']['intervalEnd']}
            """)
            summary_layout.addWidget(summary_label)
            
            # Calculate totals for different transaction types
            conversions = sum(1 for t in data['transactions'] if t['details']['type'] == 'CONVERSION')
            deposits = sum(1 for t in data['transactions'] if t['details']['type'] == 'DEPOSIT')
            transfers = sum(1 for t in data['transactions'] if t['details']['type'] == 'TRANSFER')
            
            transaction_types_label = QLabel(f"""
                Transaction Types:
                Conversions: {conversions}
                Deposits: {deposits}
                Transfers: {transfers}
            """)
            summary_layout.addWidget(transaction_types_label)
            
            # Calculate total fees
            total_fees = sum(t['totalFees']['value'] for t in data['transactions'] 
                           if t['totalFees']['currency'] == data['endOfStatementBalance']['currency'])
            fees_label = QLabel(f"Total Fees: {total_fees:,.2f} {data['endOfStatementBalance']['currency']}")
            summary_layout.addWidget(fees_label)
            
            # Add totals for credits and debits
            total_credits = sum(t['amount']['value'] for t in data['transactions'] 
                              if t['type'] == 'CREDIT' and t['amount']['currency'] == data['endOfStatementBalance']['currency'])
            total_debits = sum(abs(t['amount']['value']) for t in data['transactions'] 
                             if t['type'] == 'DEBIT' and t['amount']['currency'] == data['endOfStatementBalance']['currency'])
            
            totals_label = QLabel(f"""
                Totals ({data['endOfStatementBalance']['currency']}):
                Total Credits: {total_credits:,.2f}
                Total Debits: {total_debits:,.2f}
            """)
            summary_layout.addWidget(totals_label)
            
            self.formatted_layout.addLayout(summary_layout)

            # Switch to the formatted tab
            self.tabs.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error displaying statement: {str(e)}')
            self.status_label.setText("Error displaying statement!")

def main():
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the application
    ex = WiseAPITester()
    ex.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()