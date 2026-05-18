"""Integration with other agent systems"""
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class WorkflowAuditorIntegration:
    """Pull data from Workflow Auditor"""

    async def get_workflow_analysis(self, workflow_id: str) -> Optional[dict]:
        """
        Get workflow analysis by ID

        Args:
            workflow_id: ID of analyzed workflow

        Returns:
            Workflow analysis data or None
        """

        # In production:
        # from workflow_auditor.storage import get_workflow
        # return await get_workflow(workflow_id)

        return None

    async def get_solutions(self, workflow_id: str) -> Optional[dict]:
        """
        Get generated solutions for workflow

        Args:
            workflow_id: ID of analyzed workflow

        Returns:
            Solutions data or None
        """

        # In production:
        # from workflow_auditor.storage import get_solutions
        # return await get_solutions(workflow_id)

        return None

class LeadEnrichmentIntegration:
    """Pull data from Lead Enrichment"""

    async def get_enriched_lead(self, lead_id: str) -> Optional[dict]:
        """
        Get enriched lead data

        Args:
            lead_id: Lead ID

        Returns:
            Enriched lead data or None
        """

        # In production:
        # from lead_enrichment.storage import get_lead
        # return await get_lead(lead_id)

        return None

class SecondBrainIntegration:
    """Pull case studies and knowledge from Second Brain"""

    async def search_case_studies(
        self,
        industry: str,
        service_type: str,
        limit: int = 3
    ) -> list[dict]:
        """
        Search for relevant case studies

        Args:
            industry: Industry vertical
            service_type: Type of service
            limit: Max results

        Returns:
            List of case study documents
        """

        # In production:
        # from second_brain.query.search import brain_search
        # query = f"case study {industry} {service_type}"
        # return await brain_search(query, limit=limit)

        return []

    async def get_similar_projects(
        self,
        description: str,
        limit: int = 5
    ) -> list[dict]:
        """
        Find similar past projects

        Args:
            description: Project description
            limit: Max results

        Returns:
            List of similar projects
        """

        # In production: semantic search in Second Brain
        return []

# Mock data for testing
MOCK_WORKFLOW_ANALYSIS = {
    "workflow_id": "wf_001",
    "workflow_name": "Client Onboarding",
    "vertical": "Legal Services",
    "steps": [
        {
            "name": "Intake Form",
            "time_minutes": 30,
            "manual": True,
            "pain_points": ["Manual data entry", "Incomplete forms"]
        },
        {
            "name": "Conflict Check",
            "time_minutes": 45,
            "manual": True,
            "pain_points": ["Manual database searches"]
        },
        {
            "name": "Engagement Letter",
            "time_minutes": 60,
            "manual": True,
            "pain_points": ["Template copy/paste", "Version control"]
        }
    ],
    "total_time_minutes": 135,
    "annual_cost": 28000,
    "frequency_per_month": 15
}

MOCK_SOLUTIONS = {
    "solution_2_balanced": {
        "name": "Smart Intake & Conflict Check",
        "automation_level": 0.68,
        "tools": ["Make.com", "Claude API", "CRM Integration"],
        "estimated_outcomes": {
            "time_saved_per_cycle_minutes": 92,
            "new_cycle_time_minutes": 43,
            "time_savings_percent": 0.68,
            "annual_savings": 19040
        },
        "build_cost": {
            "your_hours": 40,
            "your_cost": 6000,
            "tool_setup": 1200,
            "total": 7200,
            "payback_months": 4.5
        },
        "timeline_weeks": 4
    }
}

MOCK_ENRICHED_LEAD = {
    "company": {
        "name": "Smith & Associates Law",
        "industry": "Legal Services",
        "employee_count": 28,
        "revenue_range": "$5M-$10M",
        "technologies": ["Clio", "QuickBooks", "Microsoft 365"]
    },
    "person": {
        "full_name": "Jennifer Smith",
        "title": "Managing Partner",
        "seniority_level": "c_level"
    },
    "score": {
        "overall_score": 87,
        "grade": "B"
    },
    "key_insights": [
        "Perfect ICP fit — mid-sized law firm with proven budget",
        "Using Clio indicates tech-forward mindset",
        "Managing Partner = direct decision maker"
    ]
}

def get_mock_workflow_analysis() -> dict:
    """Get mock workflow analysis for testing"""
    return MOCK_WORKFLOW_ANALYSIS

def get_mock_solutions() -> dict:
    """Get mock solutions for testing"""
    return MOCK_SOLUTIONS

def get_mock_enriched_lead() -> dict:
    """Get mock enriched lead for testing"""
    return MOCK_ENRICHED_LEAD
