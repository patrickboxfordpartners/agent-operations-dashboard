"""Plaid integration for bank transactions"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from shared.models import Transaction
from shared.config import config

# Plaid SDK would be imported here
# from plaid import Client
# For now, mock implementation

class PlaidClient:
    """Fetches transactions from bank accounts via Plaid"""

    def __init__(self):
        """Initialize with API credentials"""
        # In production:
        # self.client = Client(
        #     client_id=config.PLAID_CLIENT_ID,
        #     secret=config.PLAID_SECRET,
        #     environment=config.PLAID_ENV
        # )
        pass

    async def get_transactions(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[Transaction]:
        """
        Fetch transactions from Plaid

        Args:
            access_token: Plaid access token for the account
            start_date: Start date (defaults to 30 days ago)
            end_date: End date (defaults to today)

        Returns:
            List of Transaction objects
        """

        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # In production:
        # response = self.client.Transactions.get(
        #     access_token,
        #     start_date.strftime('%Y-%m-%d'),
        #     end_date.strftime('%Y-%m-%d')
        # )
        #
        # return [
        #     Transaction(
        #         id=txn['transaction_id'],
        #         date=datetime.strptime(txn['date'], '%Y-%m-%d'),
        #         amount=Decimal(str(txn['amount'])),
        #         description=txn['name'],
        #         merchant=txn.get('merchant_name'),
        #         account_id=txn['account_id'],
        #         account_type=self._map_account_type(txn['account_id']),
        #         category_plaid=txn.get('category'),
        #         merchant_name=txn.get('merchant_name'),
        #         payment_channel=txn.get('payment_channel')
        #     )
        #     for txn in response['transactions']
        # ]

        return []

    def _map_account_type(self, account_id: str) -> str:
        """Map Plaid account type to our enum"""
        # Implementation would query account details
        return "checking"

# Mock data for testing
MOCK_TRANSACTIONS = [
    {
        "id": "txn_001",
        "date": "2026-04-20",
        "amount": "127.45",
        "description": "AMZN Mktp US*2X4Y7Z",
        "merchant": "Amazon",
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Shops", "Computers and Electronics"],
        "merchant_name": "Amazon",
        "payment_channel": "online"
    },
    {
        "id": "txn_002",
        "date": "2026-04-19",
        "amount": "2500.00",
        "description": "ACH DEPOSIT PAYROLL",
        "merchant": None,
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Bank Fees", "Overdraft"],
        "merchant_name": None,
        "payment_channel": "other"
    },
    {
        "id": "txn_003",
        "date": "2026-04-18",
        "amount": "45.00",
        "description": "DROPBOX SUBSCRIPTION",
        "merchant": "Dropbox",
        "account_id": "acc_credit_001",
        "account_type": "credit_card",
        "category_plaid": ["Service", "Software"],
        "merchant_name": "Dropbox",
        "payment_channel": "online"
    },
    {
        "id": "txn_004",
        "date": "2026-04-17",
        "amount": "89.50",
        "description": "SHELL OIL 57543985",
        "merchant": "Shell",
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Transportation", "Gas Stations"],
        "merchant_name": "Shell",
        "payment_channel": "in store"
    },
    {
        "id": "txn_005",
        "date": "2026-04-16",
        "amount": "1200.00",
        "description": "LANDLORD PROPERTY LLC",
        "merchant": None,
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Payment", "Rent"],
        "merchant_name": None,
        "payment_channel": "other"
    },
    {
        "id": "txn_006",
        "date": "2026-04-15",
        "amount": "156.78",
        "description": "KROGER #4523",
        "merchant": "Kroger",
        "account_id": "acc_credit_001",
        "account_type": "credit_card",
        "category_plaid": ["Shops", "Supermarkets and Groceries"],
        "merchant_name": "Kroger",
        "payment_channel": "in store"
    },
    {
        "id": "txn_007",
        "date": "2026-04-14",
        "amount": "29.99",
        "description": "ADOBE CREATIVE CLOUD",
        "merchant": "Adobe",
        "account_id": "acc_credit_001",
        "account_type": "credit_card",
        "category_plaid": ["Service", "Software"],
        "merchant_name": "Adobe",
        "payment_channel": "online"
    },
    {
        "id": "txn_008",
        "date": "2026-04-13",
        "amount": "75.00",
        "description": "AT&T WIRELESS",
        "merchant": "AT&T",
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Bills and Utilities", "Phone"],
        "merchant_name": "AT&T",
        "payment_channel": "online"
    },
    {
        "id": "txn_009",
        "date": "2026-04-12",
        "amount": "450.00",
        "description": "INSURANCE PREMIUM",
        "merchant": "State Farm",
        "account_id": "acc_checking_001",
        "account_type": "checking",
        "category_plaid": ["Service", "Insurance"],
        "merchant_name": "State Farm",
        "payment_channel": "online"
    },
    {
        "id": "txn_010",
        "date": "2026-04-11",
        "amount": "23.45",
        "description": "STARBUCKS STORE 12345",
        "merchant": "Starbucks",
        "account_id": "acc_credit_001",
        "account_type": "credit_card",
        "category_plaid": ["Food and Drink", "Restaurants", "Coffee Shop"],
        "merchant_name": "Starbucks",
        "payment_channel": "in store"
    }
]

def get_mock_transactions() -> list[Transaction]:
    """Get mock transactions for testing"""
    return [
        Transaction(
            id=t["id"],
            date=datetime.strptime(t["date"], "%Y-%m-%d"),
            amount=Decimal(t["amount"]),
            description=t["description"],
            merchant=t["merchant"],
            account_id=t["account_id"],
            account_type=t["account_type"],
            category_plaid=t["category_plaid"],
            merchant_name=t["merchant_name"],
            payment_channel=t["payment_channel"]
        )
        for t in MOCK_TRANSACTIONS
    ]
