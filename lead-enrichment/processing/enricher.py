"""Lead enrichment orchestrator"""
from typing import Optional
from shared.models import RawLead, EnrichedLead, PersonData, CompanyData, EnrichmentScore
from shared.config import config
from integration.enrichment_apis import get_mock_enrichment
from processing.scorer import LeadScorer

class LeadEnricher:
    """Orchestrates enrichment from multiple sources"""

    def __init__(self, anthropic_api_key: str):
        self.scorer = LeadScorer(anthropic_api_key)

        # Initialize API clients (mock for now)
        # self.clearbit = ClearbitClient()
        # self.apollo = ApolloClient()
        # self.builtwith = BuiltWithClient()
        # self.crunchbase = CrunchbaseClient()

    async def enrich_lead(
        self,
        raw_lead: RawLead,
        icp_context: str = ""
    ) -> Optional[EnrichedLead]:
        """
        Enrich a raw lead with all available data

        Args:
            raw_lead: Minimal lead info
            icp_context: Optional ICP description for scoring

        Returns:
            EnrichedLead or None if enrichment fails
        """

        data_sources = []
        cost = 0.0

        # 1. Get person data
        person_data = await self._enrich_person(raw_lead)
        if not person_data:
            return None
        data_sources.append("mock_database")

        # 2. Get company data (if we have domain)
        company_data = None
        if raw_lead.website or raw_lead.company:
            domain = raw_lead.website or self._extract_domain(raw_lead.email)
            company_data = await self._enrich_company(domain)
            if company_data:
                data_sources.append("mock_database")

        if not company_data:
            # Create minimal company data
            company_data = CompanyData(
                name=raw_lead.company or "Unknown",
                domain=self._extract_domain(raw_lead.email)
            )

        # 3. Score the lead
        score = await self.scorer.score_lead(
            person=person_data,
            company=company_data,
            icp_context=icp_context
        )
        cost += 0.05  # Claude API cost

        # 4. Generate insights
        insights = await self.scorer.generate_insights(
            person=person_data,
            company=company_data,
            score=score
        )
        cost += 0.03

        # 5. Build enriched lead
        enriched = EnrichedLead(
            raw_lead=raw_lead,
            company=company_data,
            person=person_data,
            score=score,
            key_insights=insights["key_insights"],
            recommended_approach=insights["recommended_approach"],
            talking_points=insights["talking_points"],
            enrichment_confidence=self._calculate_confidence(person_data, company_data),
            data_sources=data_sources,
            cost_usd=cost
        )

        return enriched

    async def batch_enrich(
        self,
        raw_leads: list[RawLead],
        icp_context: str = ""
    ) -> list[EnrichedLead]:
        """
        Enrich multiple leads

        Args:
            raw_leads: List of raw leads
            icp_context: Optional ICP context

        Returns:
            List of enriched leads (excludes failed enrichments)
        """

        enriched = []
        for raw_lead in raw_leads:
            try:
                result = await self.enrich_lead(raw_lead, icp_context)
                if result:
                    enriched.append(result)
            except Exception as e:
                print(f"Failed to enrich {raw_lead.email}: {e}")

        return enriched

    async def _enrich_person(self, raw_lead: RawLead) -> Optional[PersonData]:
        """Get person data from enrichment sources"""

        # Try mock data first (for testing)
        mock_data = get_mock_enrichment(raw_lead.email)
        if mock_data and "person" in mock_data:
            return mock_data["person"]

        # In production:
        # 1. Try Clearbit
        # person = await self.clearbit.enrich_person(raw_lead.email)
        # if person:
        #     return person
        #
        # 2. Try Apollo
        # person = await self.apollo.search_person(raw_lead.email)
        # if person:
        #     return person

        # Fallback: use what we have
        if raw_lead.name:
            return PersonData(
                full_name=raw_lead.name,
                email=raw_lead.email,
                title=raw_lead.title,
                linkedin_url=raw_lead.linkedin_url
            )

        return None

    async def _enrich_company(self, domain: str) -> Optional[CompanyData]:
        """Get company data from enrichment sources"""

        # Try mock data first (for testing)
        # Check all mock data for matching domain
        from integration.enrichment_apis import MOCK_ENRICHMENT_DATA
        for mock_data in MOCK_ENRICHMENT_DATA.values():
            if mock_data["company"].domain == domain:
                return mock_data["company"]

        # In production:
        # 1. Try Clearbit
        # company = await self.clearbit.enrich_company(domain)
        # if company:
        #     # Augment with tech stack
        #     tech = await self.builtwith.get_tech_stack(domain)
        #     company.tech_categories = tech
        #
        #     # Augment with funding
        #     funding = await self.crunchbase.get_funding_data(company.name)
        #     company.funding_stage = funding.get('stage')
        #     company.total_funding = funding.get('total')
        #     ...
        #
        #     return company
        #
        # 2. Try Apollo
        # company = await self.apollo.search_company(domain)

        return None

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address"""
        return email.split("@")[1] if "@" in email else ""

    def _calculate_confidence(self, person: PersonData, company: CompanyData) -> float:
        """
        Calculate confidence in enrichment data

        Based on completeness of data
        """

        confidence = 0.0

        # Person data (40% weight)
        person_fields = [
            person.title,
            person.department,
            person.seniority_level,
            person.linkedin_url,
            person.years_in_role,
            person.years_at_company
        ]
        person_completeness = sum(1 for f in person_fields if f is not None) / len(person_fields)
        confidence += person_completeness * 0.4

        # Company data (60% weight)
        company_fields = [
            company.industry,
            company.employee_count,
            company.annual_revenue,
            company.founded_year,
            company.location,
            len(company.technologies) > 0,
            company.funding_stage
        ]
        company_completeness = sum(1 for f in company_fields if f) / len(company_fields)
        confidence += company_completeness * 0.6

        return round(confidence, 2)
