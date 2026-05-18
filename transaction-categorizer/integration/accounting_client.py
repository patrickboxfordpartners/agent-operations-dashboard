"""Integration with QuickBooks/Xero"""
from typing import Literal, Optional
from shared.models import Category, CategorizedTransaction, ReconciliationResult
from shared.config import config

class AccountingClient:
    """Base class for accounting software integration"""

    async def get_chart_of_accounts(self) -> list[Category]:
        """Fetch chart of accounts"""
        raise NotImplementedError

    async def post_transaction(self, transaction: CategorizedTransaction) -> str:
        """Post categorized transaction to accounting software"""
        raise NotImplementedError

    async def reconcile(self, transaction: CategorizedTransaction) -> ReconciliationResult:
        """Check if transaction already exists (duplicate detection)"""
        raise NotImplementedError

class QuickBooksClient(AccountingClient):
    """QuickBooks integration"""

    def __init__(self):
        """Initialize with OAuth credentials"""
        # In production:
        # self.client = QuickBooks(
        #     client_id=config.QUICKBOOKS_CLIENT_ID,
        #     client_secret=config.QUICKBOOKS_CLIENT_SECRET,
        #     realm_id=config.QUICKBOOKS_REALM_ID
        # )
        pass

    async def get_chart_of_accounts(self) -> list[Category]:
        """Fetch chart of accounts from QuickBooks"""
        # In production:
        # accounts = self.client.query("SELECT * FROM Account")
        # return [
        #     Category(
        #         id=acc['Id'],
        #         name=acc['Name'],
        #         account_type=self._map_account_type(acc['AccountType']),
        #         parent_id=acc.get('ParentRef', {}).get('value'),
        #         tax_category=acc.get('TaxCodeRef', {}).get('value')
        #     )
        #     for acc in accounts
        # ]

        return []

    async def post_transaction(self, transaction: CategorizedTransaction) -> str:
        """Post to QuickBooks as expense/income"""
        # Implementation would use QuickBooks API
        return "qb_txn_001"

    async def reconcile(self, transaction: CategorizedTransaction) -> ReconciliationResult:
        """Check for duplicates in QuickBooks"""
        # Query by date, amount, description
        # Return match status
        return ReconciliationResult(
            transaction_id=transaction.transaction.id,
            status="new"
        )

class XeroClient(AccountingClient):
    """Xero integration"""

    def __init__(self):
        """Initialize with OAuth credentials"""
        pass

    async def get_chart_of_accounts(self) -> list[Category]:
        """Fetch chart of accounts from Xero"""
        return []

    async def post_transaction(self, transaction: CategorizedTransaction) -> str:
        """Post to Xero"""
        return "xero_txn_001"

    async def reconcile(self, transaction: CategorizedTransaction) -> ReconciliationResult:
        """Check for duplicates in Xero"""
        return ReconciliationResult(
            transaction_id=transaction.transaction.id,
            status="new"
        )

# Mock chart of accounts for testing
MOCK_CATEGORIES = [
    Category(
        id="cat_001",
        name="Office Supplies",
        account_type="expense",
        keywords=["supplies", "paper", "pens", "staples", "office"],
        merchant_patterns=["staples", "office depot", "amazon"]
    ),
    Category(
        id="cat_002",
        name="Software & Subscriptions",
        account_type="expense",
        keywords=["software", "subscription", "saas", "cloud"],
        merchant_patterns=["adobe", "dropbox", "microsoft", "google"]
    ),
    Category(
        id="cat_003",
        name="Meals & Entertainment",
        account_type="expense",
        keywords=["restaurant", "coffee", "lunch", "dinner"],
        merchant_patterns=["starbucks", "chipotle", "restaurant"]
    ),
    Category(
        id="cat_004",
        name="Travel & Vehicle",
        account_type="expense",
        keywords=["gas", "fuel", "mileage", "parking", "travel"],
        merchant_patterns=["shell", "exxon", "chevron", "uber", "lyft"]
    ),
    Category(
        id="cat_005",
        name="Rent & Lease",
        account_type="expense",
        keywords=["rent", "lease", "landlord"],
        merchant_patterns=["property", "landlord", "realty"]
    ),
    Category(
        id="cat_006",
        name="Utilities",
        account_type="expense",
        keywords=["electric", "gas", "water", "phone", "internet"],
        merchant_patterns=["at&t", "verizon", "comcast"]
    ),
    Category(
        id="cat_007",
        name="Insurance",
        account_type="expense",
        keywords=["insurance", "premium"],
        merchant_patterns=["state farm", "geico", "allstate"]
    ),
    Category(
        id="cat_008",
        name="Client Revenue",
        account_type="income",
        keywords=["payment", "invoice", "revenue"],
        merchant_patterns=[]
    ),
    Category(
        id="cat_009",
        name="Owner Draw",
        account_type="equity",
        keywords=["draw", "distribution", "owner"],
        merchant_patterns=[]
    ),
    Category(
        id="cat_010",
        name="Uncategorized",
        account_type="expense",
        keywords=[],
        merchant_patterns=[]
    )
]

def get_mock_categories() -> list[Category]:
    """Get mock chart of accounts for testing"""
    return MOCK_CATEGORIES
