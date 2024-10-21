import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
import requests
import json

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
        self.currency_input.setText('EUR')
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
        self.end_date_input.setText('2023-08-31T23:59:59.999Z')
        date_layout.addWidget(self.end_date_input)
        layout.addLayout(date_layout)

        # Fetch Statement Button
        self.fetch_button = QPushButton('Fetch Statement')
        self.fetch_button.clicked.connect(self.fetch_statement)
        layout.addWidget(self.fetch_button)

        # Result Display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.setLayout(layout)
        self.setWindowTitle('Wise API Tester')
        self.setGeometry(300, 300, 600, 400)

    def fetch_balances(self):
        token = self.token_input.text()
        profile_id = self.profile_input.text()

        if not all([token, profile_id]):
            QMessageBox.warning(self, 'Input Error', 'Please enter API Token and Profile ID.')
            return

        url = f"https://api.sandbox.transferwise.tech/v1/borderless-accounts?profileId={profile_id}"
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
            QMessageBox.critical(self, 'API Error', str(e))

    def fetch_statement(self):
        token = self.token_input.text()
        profile_id = self.profile_input.text()
        balance_id = self.balance_dropdown.currentData()
        currency = self.currency_input.text()
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()

        if not all([token, profile_id, balance_id, currency, start_date, end_date]):
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields and fetch balances.')
            return

        url = f"https://api.sandbox.transferwise.tech/v3/profiles/{profile_id}/balance-statements/{balance_id}/statement.json"
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
            response.raise_for_status()
            data = response.json()
            self.result_display.setPlainText(json.dumps(data, indent=2))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'API Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WiseAPITester()
    ex.show()
    sys.exit(app.exec_())
