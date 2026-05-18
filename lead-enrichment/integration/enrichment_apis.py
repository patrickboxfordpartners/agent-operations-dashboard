"""Integration with enrichment data providers"""
from typing import Optional
from shared.models import CompanyData, PersonData, RawLead
from shared.config import config

class ClearbitClient:
    """Clearbit enrichment API"""

    def __init__(self):
        # In production: import clearbit; clearbit.key = config.CLEARBIT_API_KEY
        pass

    async def enrich_company(self, domain: str) -> Optional[CompanyData]:
        """
        Enrich company data from domain

        Args:
            domain: Company website domain

        Returns:
            CompanyData or None if not found
        """
        # In production:
        # try:
        #     company = clearbit.Company.find(domain=domain)
        #     return CompanyData(
        #         name=company['name'],
        #         domain=company['domain'],
        #         industry=company.get('category', {}).get('industry'),
        #         employee_count=company.get('metrics', {}).get('employees'),
        #         ...
        #     )
        # except clearbit.NotFoundError:
        #     return None

        return None

    async def enrich_person(self, email: str) -> Optional[PersonData]:
        """
        Enrich person data from email

        Args:
            email: Person's email address

        Returns:
            PersonData or None if not found
        """
        # In production:
        # person = clearbit.Person.find(email=email)
        # return PersonData(...)

        return None

class ApolloClient:
    """Apollo.io API for B2B data"""

    def __init__(self):
        pass

    async def search_person(self, email: str) -> Optional[PersonData]:
        """Find person by email"""
        return None

    async def search_company(self, domain: str) -> Optional[CompanyData]:
        """Find company by domain"""
        return None

class BuiltWithClient:
    """BuiltWith API for tech stack detection"""

    def __init__(self):
        pass

    async def get_tech_stack(self, domain: str) -> dict[str, list[str]]:
        """
        Get technologies used by a domain

        Returns:
            Dict mapping category to list of technologies
            Example: {"CRM": ["Salesforce"], "Analytics": ["Google Analytics"]}
        """
        # In production: call BuiltWith API
        return {}

class CrunchbaseClient:
    """Crunchbase API for funding data"""

    def __init__(self):
        pass

    async def get_funding_data(self, company_name: str) -> dict:
        """
        Get funding information

        Returns:
            Dict with funding_stage, total_funding, last_funding_date
        """
        return {}

# Mock data for testing
MOCK_ENRICHMENT_DATA = {
    "john.smith@acmecorp.com": {
        "person": PersonData(
            full_name="John Smith",
            email="john.smith@acmecorp.com",
            title="VP of Operations",
            department="Operations",
            seniority_level="senior",
            linkedin_url="https://linkedin.com/in/johnsmith",
            years_in_role=2,
            years_at_company=5,
            previous_companies=["TechCorp", "InnovateLabs"]
        ),
        "company": CompanyData(
            name="ACME Corp",
            domain="acmecorp.com",
            industry="Professional Services",
            employee_count=75,
            employee_range="51-200",
            annual_revenue=8_000_000,
            revenue_range="$5M-$10M",
            founded_year=2010,
            location="Austin, TX",
            description="Management consulting firm specializing in process optimization",
            technologies=["Salesforce", "QuickBooks", "Slack", "Microsoft 365", "HubSpot"],
            tech_categories={
                "CRM": ["Salesforce", "HubSpot"],
                "Accounting": ["QuickBooks"],
                "Collaboration": ["Slack", "Microsoft 365"]
            },
            funding_stage="bootstrapped",
            linkedin_url="https://linkedin.com/company/acmecorp",
            linkedin_followers=1250
        )
    },
    "sarah.johnson@techstartup.io": {
        "person": PersonData(
            full_name="Sarah Johnson",
            email="sarah.johnson@techstartup.io",
            title="CEO & Founder",
            department="Executive",
            seniority_level="c_level",
            linkedin_url="https://linkedin.com/in/sarahjohnson",
            twitter_handle="@sarahj",
            years_in_role=3,
            years_at_company=3,
            previous_companies=["Google", "Stripe"]
        ),
        "company": CompanyData(
            name="TechStartup.io",
            domain="techstartup.io",
            industry="Technology",
            employee_count=25,
            employee_range="11-50",
            annual_revenue=2_500_000,
            revenue_range="$1M-$5M",
            founded_year=2021,
            location="San Francisco, CA",
            description="SaaS platform for workflow automation",
            technologies=["AWS", "React", "PostgreSQL", "Stripe"],
            tech_categories={
                "Infrastructure": ["AWS"],
                "Frontend": ["React"],
                "Database": ["PostgreSQL"],
                "Payments": ["Stripe"]
            },
            funding_stage="series_a",
            total_funding=5_000_000,
            last_funding_date="2023-08-15",
            linkedin_url="https://linkedin.com/company/techstartupio",
            linkedin_followers=850,
            twitter_handle="@techstartupio"
        )
    },
    "mike.brown@locallaw.com": {
        "person": PersonData(
            full_name="Mike Brown",
            email="mike.brown@locallaw.com",
            title="Office Manager",
            department="Operations",
            seniority_level="mid",
            linkedin_url="https://linkedin.com/in/mikebrown",
            years_in_role=4,
            years_at_company=4,
            previous_companies=["Legal Services Inc"]
        ),
        "company": CompanyData(
            name="Local Law Firm",
            domain="locallaw.com",
            industry="Legal Services",
            employee_count=12,
            employee_range="11-50",
            annual_revenue=1_500_000,
            revenue_range="$1M-$5M",
            founded_year=2005,
            location="Denver, CO",
            description="Family law and estate planning practice",
            technologies=["Clio", "Microsoft 365", "QuickBooks"],
            tech_categories={
                "Practice Management": ["Clio"],
                "Office": ["Microsoft 365"],
                "Accounting": ["QuickBooks"]
            },
            funding_stage="bootstrapped",
            linkedin_url="https://linkedin.com/company/locallawfirm",
            linkedin_followers=320
        )
    },
    "emily.davis@bigcorp.com": {
        "person": PersonData(
            full_name="Emily Davis",
            email="emily.davis@bigcorp.com",
            title="IT Manager",
            department="IT",
            seniority_level="mid",
            linkedin_url="https://linkedin.com/in/emilydavis",
            years_in_role=1,
            years_at_company=8,
            previous_companies=["MegaCorp"]
        ),
        "company": CompanyData(
            name="BigCorp Industries",
            domain="bigcorp.com",
            industry="Manufacturing",
            employee_count=2500,
            employee_range="1001-5000",
            annual_revenue=250_000_000,
            revenue_range="$100M+",
            founded_year=1985,
            location="Chicago, IL",
            description="Industrial manufacturing and distribution",
            technologies=["SAP", "Oracle", "Salesforce"],
            tech_categories={
                "ERP": ["SAP", "Oracle"],
                "CRM": ["Salesforce"]
            },
            funding_stage="public",
            linkedin_url="https://linkedin.com/company/bigcorp",
            linkedin_followers=15000
        )
    },
    "alex.martinez@solopreneur.com": {
        "person": PersonData(
            full_name="Alex Martinez",
            email="alex.martinez@solopreneur.com",
            title="Founder",
            department="Executive",
            seniority_level="c_level",
            linkedin_url="https://linkedin.com/in/alexmartinez",
            years_in_role=1,
            years_at_company=1,
            previous_companies=[]
        ),
        "company": CompanyData(
            name="Solo Consulting",
            domain="solopreneur.com",
            industry="Consulting",
            employee_count=1,
            employee_range="1-10",
            annual_revenue=150_000,
            revenue_range="$100K-$500K",
            founded_year=2023,
            location="Remote",
            description="Independent business consultant",
            technologies=["Gmail", "Google Workspace"],
            tech_categories={
                "Email": ["Gmail"],
                "Office": ["Google Workspace"]
            },
            funding_stage="bootstrapped",
            linkedin_url="https://linkedin.com/in/alexmartinez",
            linkedin_followers=450
        )
    }
}

def get_mock_enrichment(email: str) -> Optional[dict]:
    """Get mock enrichment data for testing"""
    return MOCK_ENRICHMENT_DATA.get(email)
