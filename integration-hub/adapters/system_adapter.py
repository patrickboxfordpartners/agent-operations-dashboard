"""Base adapter for connecting to individual systems"""
from abc import ABC, abstractmethod
from typing import Optional, Any
import sys
from pathlib import Path

class SystemAdapter(ABC):
    """Base class for system adapters"""

    def __init__(self, system_name: str, system_path: Path):
        self.system_name = system_name
        self.system_path = system_path
        self._add_to_path()

    def _add_to_path(self):
        """Add system to Python path for imports"""
        if str(self.system_path) not in sys.path:
            sys.path.insert(0, str(self.system_path))

    @abstractmethod
    async def enrich_lead(self, lead_data: dict) -> dict:
        """Enrich a lead"""
        pass

    @abstractmethod
    async def analyze_workflow(self, workflow_description: str) -> dict:
        """Analyze a workflow"""
        pass

    @abstractmethod
    async def generate_proposal(self, lead_data: dict, workflow_data: dict) -> dict:
        """Generate a proposal"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if system is available"""
        pass


class LeadEnrichmentAdapter(SystemAdapter):
    """Adapter for Lead Enrichment system"""

    def __init__(self, system_name: str, system_path: Path):
        super().__init__(system_name, system_path)
        # Pre-import to validate availability
        try:
            sys.path.insert(0, str(system_path))
            import shared.models
            import processing.enricher
            self._available = True
        except ImportError as e:
            self._available = False
            self._import_error = str(e)

    async def enrich_lead(self, lead_data: dict) -> dict:
        """
        Enrich lead with company and person data

        Args:
            lead_data: {"email": "...", "name": "...", "company": "..."}

        Returns:
            Enriched lead data with score, grade, insights
        """

        if not self._available:
            return {"error": f"Lead Enrichment not available: {self._import_error}"}

        try:
            # Import from the system path
            sys.path.insert(0, str(self.system_path))
            from shared.models import RawLead
            from processing.enricher import LeadEnricher
            import os

            # Create RawLead
            raw_lead = RawLead(
                id=lead_data.get("id", "lead_temp"),
                email=lead_data["email"],
                name=lead_data.get("name"),
                company=lead_data.get("company"),
                title=lead_data.get("title"),
                source=lead_data.get("source", "integration_hub")
            )

            # Enrich
            api_key = os.getenv("ANTHROPIC_API_KEY")
            enricher = LeadEnricher(api_key)
            enriched = await enricher.enrich_lead(raw_lead)

            return {
                "score": enriched.score.overall_score,
                "grade": enriched.score.grade,
                "company": enriched.company.model_dump() if enriched.company else None,
                "person": enriched.person.model_dump(),
                "key_insights": enriched.key_insights,
                "recommended_approach": enriched.recommended_approach,
                "talking_points": enriched.talking_points,
                "confidence": enriched.enrichment_confidence
            }

        except Exception as e:
            return {"error": str(e)}

    async def analyze_workflow(self, workflow_description: str) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def generate_proposal(self, lead_data: dict, workflow_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check if Lead Enrichment is available"""
        return self._available


class WorkflowAuditorAdapter(SystemAdapter):
    """Adapter for Workflow Auditor system"""

    def __init__(self, system_name: str, system_path: Path):
        super().__init__(system_name, system_path)
        try:
            # Temporarily adjust path for isolated import
            old_path = sys.path.copy()
            sys.path = [str(system_path)] + sys.path
            import processing.workflow_extractor
            import processing.solution_generator
            sys.path = old_path
            self._available = True
        except Exception as e:
            self._available = False
            self._import_error = str(e)
            sys.path = old_path if 'old_path' in locals() else sys.path

    async def analyze_workflow(self, workflow_description: str) -> dict:
        """
        Analyze a workflow

        Args:
            workflow_description: Text description of workflow

        Returns:
            Workflow analysis and solutions
        """

        if not self._available:
            return {"error": f"Workflow Auditor not available: {self._import_error}"}

        try:
            sys.path.insert(0, str(self.system_path))
            from processing.workflow_extractor import extractor
            from processing.solution_generator import generator
            import os

            # Extract workflow structure
            analysis = await extractor.extract(workflow_description, vertical="General")

            # Generate solutions
            solutions = await generator.generate(
                workflow=analysis,
                vertical="General"
            )

            return {
                "analysis": analysis.model_dump(),
                "solutions": {
                    k: v.model_dump() if hasattr(v, 'model_dump') else v
                    for k, v in solutions.items()
                    if k.startswith('solution_')
                },
                "recommended": solutions.get("recommended_solution"),
                "reasoning": solutions.get("recommendation_reasoning")
            }

        except Exception as e:
            return {"error": str(e)}

    async def enrich_lead(self, lead_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def generate_proposal(self, lead_data: dict, workflow_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check if Workflow Auditor is available"""
        return self._available


class ProposalBuilderAdapter(SystemAdapter):
    """Adapter for Proposal Builder system"""

    def __init__(self, system_name: str, system_path: Path):
        super().__init__(system_name, system_path)
        try:
            sys.path.insert(0, str(system_path))
            import shared.models
            import processing.generator
            self._available = True
        except ImportError as e:
            self._available = False
            self._import_error = str(e)

    async def generate_proposal(self, lead_data: dict, workflow_data: dict = None) -> dict:
        """
        Generate a proposal

        Args:
            lead_data: Lead/client information
            workflow_data: Optional workflow analysis

        Returns:
            Generated proposal
        """

        if not self._available:
            return {"error": f"Proposal Builder not available: {self._import_error}"}

        try:
            sys.path.insert(0, str(self.system_path))
            from shared.models import ProposalRequest, ClientInfo, DiscoveryNotes, AutomationInputs
            from processing.generator import ProposalGenerator
            import os

            # Build request
            client = ClientInfo(
                company_name=lead_data["company"],
                contact_name=lead_data["name"],
                contact_email=lead_data["email"],
                industry=lead_data.get("industry"),
                company_size=lead_data.get("company_size")
            )

            discovery = DiscoveryNotes(
                pain_points=lead_data.get("pain_points", []),
                goals=lead_data.get("goals", []),
                notes=lead_data.get("notes", "")
            )

            automation_inputs = None
            if workflow_data:
                automation_inputs = AutomationInputs(
                    workflow_analysis=workflow_data.get("analysis"),
                    workflow_solutions=workflow_data.get("solutions")
                )

            request = ProposalRequest(
                service_type="ai_automation",
                client=client,
                discovery=discovery,
                automation_inputs=automation_inputs
            )

            # Generate
            api_key = os.getenv("ANTHROPIC_API_KEY")
            generator = ProposalGenerator(api_key)
            proposal = await generator.generate(request)

            return proposal.model_dump()

        except Exception as e:
            return {"error": str(e)}

    async def enrich_lead(self, lead_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def analyze_workflow(self, workflow_description: str) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check if Proposal Builder is available"""
        return self._available


class MercuryIntelligenceAdapter(SystemAdapter):
    """Adapter for Mercury Intelligence system"""

    def __init__(self, system_name: str, system_path: Path):
        super().__init__(system_name, system_path)
        try:
            sys.path.insert(0, str(system_path))
            import shared.models
            import processing.categorizer
            self._available = True
        except ImportError as e:
            self._available = False
            self._import_error = str(e)

    async def categorize_transaction(self, transaction_data: dict) -> dict:
        """
        Categorize a Mercury transaction

        Args:
            transaction_data: Transaction details

        Returns:
            Categorized transaction with flags
        """

        if not self._available:
            return {"error": f"Mercury Intelligence not available: {self._import_error}"}

        try:
            sys.path.insert(0, str(self.system_path))
            from shared.models import MercuryTransaction
            from processing.categorizer import MercuryCategorizer
            from datetime import datetime
            from decimal import Decimal
            import os

            # Build transaction
            txn = MercuryTransaction(
                id=transaction_data["id"],
                status=transaction_data["status"],
                amount=Decimal(str(transaction_data["amount"])),
                bank_description=transaction_data["description"],
                counterparty_name=transaction_data.get("merchant"),
                created_at=datetime.fromisoformat(transaction_data["date"]),
                kind=transaction_data.get("kind", "other"),
                account_id=transaction_data.get("account_id", "default")
            )

            # Categorize
            api_key = os.getenv("ANTHROPIC_API_KEY")
            categorizer = MercuryCategorizer(api_key, categories=[])
            categorized = await categorizer.categorize(txn)

            return categorized.model_dump()

        except Exception as e:
            return {"error": str(e)}

    async def enrich_lead(self, lead_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def analyze_workflow(self, workflow_description: str) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def generate_proposal(self, lead_data: dict, workflow_data: dict) -> dict:
        """Not applicable for this adapter"""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Check if Mercury Intelligence is available"""
        return self._available
