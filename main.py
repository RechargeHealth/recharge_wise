import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QScrollArea
from PyQt5.QtCore import Qt
import requests

class WiseAPITester(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # API Token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel('API Token:'))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)

        # Profile ID
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel('Profile ID:'))
        self.profile_input = QLineEdit()
        profile_layout.addWidget(self.profile_input)
        layout.addLayout(profile_layout)

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

        # Tabs for displaying results
        self.tabs = QTabWidget()
        self.raw_result_display = QTextEdit()
        self.raw_result_display.setReadOnly(True)
        self.tabs.addTab(self.raw_result_display, "Raw JSON")

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
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.balance_dropdown.clear()
            for account in data:
                for balance in account['balances']:
                    self.balance_dropdown.addItem(f"{balance['id']} ({balance['currency']})", balance['id'])
            
            QMessageBox.information(self, 'Success', 'Balances fetched successfully!')
        except requests.exceptions.RequestException as e:
            error_message = f"API Error: {str(e)}\n\nURL: {url}\n\nHeaders: {dict(e.response.headers) if e.response else 'No headers'}\n\nResponse: {e.response.text if e.response else 'No response'}"
            QMessageBox.critical(self, 'API Error', error_message)
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
            response = requests.get(url, params=params, headers=headers)
            self.raw_result_display.setPlainText(f"Status Code: {response.status_code}\n\nHeaders: {dict(response.headers)}\n\nResponse:\n{response.text}")
            response.raise_for_status()
            data = response.json()
            self.raw_result_display.setPlainText(json.dumps(data, indent=2))
            self.display_formatted_statement(data)
        except requests.exceptions.RequestException as e:
            error_message = f"API Error: {str(e)}\n\nURL: {url}\n\nParams: {params}\n\nHeaders: {dict(e.response.headers) if e.response else 'No headers'}\n\nResponse: {e.response.text if e.response else 'No response'}"
            QMessageBox.critical(self, 'API Error', error_message)
            self.raw_result_display.setPlainText(error_message)

    def display_formatted_statement(self, data):
        # Clear previous content
        for i in reversed(range(self.formatted_layout.count())): 
            self.formatted_layout.itemAt(i).widget().setParent(None)

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
        transactions_table.setHorizontalHeaderLabels(["Date", "Type", "Amount", "Currency", "Description", "Fees", "Transaction Details", "Exchange Rate", "Running Balance", "Reference", "Recipient"])
        transactions_table.setRowCount(len(data['transactions']))

        for row, transaction in enumerate(data['transactions']):
            transactions_table.setItem(row, 0, QTableWidgetItem(transaction['date']))
            transactions_table.setItem(row, 1, QTableWidgetItem(transaction['type']))
            transactions_table.setItem(row, 2, QTableWidgetItem(str(transaction['amount']['value'])))
            transactions_table.setItem(row, 3, QTableWidgetItem(transaction['amount']['currency']))
            transactions_table.setItem(row, 4, QTableWidgetItem(transaction['details']['description']))
            
            # Fees
            fees = transaction['totalFees']['value'] if transaction['totalFees']['value'] != 0 else '-'
            transactions_table.setItem(row, 5, QTableWidgetItem(str(fees)))
            
            # Transaction Details
            if transaction['details']['type'] == 'CONVERSION':
                details = f"From: {transaction['details']['sourceAmount']['value']} {transaction['details']['sourceAmount']['currency']}\n"
                details += f"To: {transaction['details']['targetAmount']['value']} {transaction['details']['targetAmount']['currency']}"
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
                exchange_rate = str(transaction['exchangeDetails']['rate'])
            elif 'rate' in transaction['details']:
                exchange_rate = str(transaction['details']['rate'])
            transactions_table.setItem(row, 7, QTableWidgetItem(exchange_rate))
            
            # Running Balance
            running_balance = f"{transaction['runningBalance']['value']} {transaction['runningBalance']['currency']}"
            transactions_table.setItem(row, 8, QTableWidgetItem(running_balance))

            # Reference Number
            transactions_table.setItem(row, 9, QTableWidgetItem(transaction['referenceNumber']))

            # Recipient
            recipient = transaction['details'].get('recipient', {})
            recipient_info = f"{recipient.get('name', 'N/A')}\n{recipient.get('bankAccount', 'N/A')}" if recipient else '-'
            transactions_table.setItem(row, 10, QTableWidgetItem(recipient_info))

        transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        transactions_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.formatted_layout.addWidget(transactions_table)

        # Switch to the formatted tab
        self.tabs.setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WiseAPITester()
    ex.show()
    sys.exit(app.exec_())