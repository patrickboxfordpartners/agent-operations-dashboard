"""Lead-to-Proposal workflow orchestration"""
import asyncio
from datetime import datetime
from typing import Optional

from core.models import Lead, LeadStatus, Event, EventType, EntityType, WorkflowExecution
from adapters.system_adapter import (
    LeadEnrichmentAdapter,
    WorkflowAuditorAdapter,
    ProposalBuilderAdapter
)
from core.config import config

class LeadToProposalWorkflow:
    """
    Orchestrates the full lead-to-proposal pipeline:

    1. Lead comes in (form, LinkedIn, referral)
    2. Lead Enrichment: Score and enrich with company data
    3. If Grade A/B: Continue, else route to nurture
    4. Workflow Auditor: Analyze their current process
    5. Proposal Builder: Generate custom proposal
    6. Lead Nurture: Send proposal and track engagement
    """

    def __init__(self):
        self.enrichment_adapter = LeadEnrichmentAdapter(
            "lead-enrichment",
            config.SYSTEMS["lead-enrichment"]
        )
        self.workflow_adapter = WorkflowAuditorAdapter(
            "workflow-auditor",
            config.SYSTEMS["workflow-auditor"]
        )
        self.proposal_adapter = ProposalBuilderAdapter(
            "proposal-builder",
            config.SYSTEMS["proposal-builder"]
        )

    async def execute(self, lead: Lead, workflow_description: str = None) -> WorkflowExecution:
        """
        Execute the full workflow

        Args:
            lead: Lead to process
            workflow_description: Optional workflow description from discovery

        Returns:
            WorkflowExecution with results
        """

        execution = WorkflowExecution(
            id=f"exec_{datetime.now().timestamp()}",
            workflow_id="lead_to_proposal",
            trigger_event_id=f"lead_{lead.id}",
            status="running"
        )

        try:
            # Step 1: Enrich Lead
            print(f"\n📊 Step 1: Enriching lead {lead.name}...")
            enrichment_result = await self._enrich_lead(lead)
            execution.step_results.append({
                "step": "enrich_lead",
                "result": enrichment_result,
                "status": "completed"
            })

            # Update lead
            lead.enrichment_score = enrichment_result.get("score")
            lead.enrichment_grade = enrichment_result.get("grade")
            lead.enrichment_data = enrichment_result
            lead.status = LeadStatus.ENRICHED

            print(f"   ✅ Grade {lead.enrichment_grade} ({lead.enrichment_score}/100)")

            # Step 2: Check if qualified (A or B grade)
            # TEMP: Override for testing - accept C grade too
            if lead.enrichment_grade not in ["A", "B", "C"]:
                print(f"   ⚠️  Grade {lead.enrichment_grade} - routing to nurture sequence")
                execution.status = "completed"
                execution.completed_at = datetime.now()
                execution.step_results.append({
                    "step": "qualification_check",
                    "result": {"qualified": False, "reason": f"Grade {lead.enrichment_grade}"},
                    "status": "completed"
                })
                return execution

            lead.status = LeadStatus.QUALIFIED
            print(f"   ✅ Qualified for immediate outreach")

            # Step 3: Analyze Workflow (if description provided)
            workflow_result = None
            if workflow_description:
                print(f"\n🔍 Step 2: Analyzing workflow...")
                workflow_result = await self._analyze_workflow(workflow_description)
                execution.step_results.append({
                    "step": "analyze_workflow",
                    "result": workflow_result,
                    "status": "completed"
                })

                lead.workflow_analysis_id = f"wf_{datetime.now().timestamp()}"
                lead.workflow_data = workflow_result
                lead.status = LeadStatus.WORKFLOW_ANALYZED

                print(f"   ✅ Workflow analyzed")
                if workflow_result.get("solutions"):
                    recommended = workflow_result.get("recommended", "solution_2_balanced")
                    print(f"   💡 Recommended: {recommended}")

            # Step 4: Generate Proposal
            print(f"\n📝 Step 3: Generating proposal...")
            proposal_result = await self._generate_proposal(lead, workflow_result)
            execution.step_results.append({
                "step": "generate_proposal",
                "result": proposal_result,
                "status": "completed"
            })

            lead.proposal_id = proposal_result.get("proposal_id")
            lead.status = LeadStatus.PROPOSAL_SENT
            lead.proposal_sent_at = datetime.now()

            print(f"   ✅ Proposal generated: {proposal_result.get('title')}")
            print(f"   📄 Proposal ID: {lead.proposal_id}")

            # Step 5: Queue for delivery (Lead Nurture handles this)
            print(f"\n📧 Step 4: Queueing proposal for delivery...")
            execution.step_results.append({
                "step": "queue_delivery",
                "result": {
                    "lead_id": lead.id,
                    "proposal_id": lead.proposal_id,
                    "delivery_method": "email",
                    "status": "queued"
                },
                "status": "completed"
            })

            execution.status = "completed"
            execution.completed_at = datetime.now()
            execution.current_step = len(execution.step_results)

            print(f"\n✅ Workflow completed successfully")

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.now()
            print(f"\n❌ Workflow failed: {e}")

        return execution

    async def _enrich_lead(self, lead: Lead) -> dict:
        """Enrich lead via Lead Enrichment system"""

        lead_data = {
            "id": lead.id,
            "email": lead.email,
            "name": lead.name,
            "company": lead.company,
            "title": lead.title,
            "source": lead.source
        }

        return await self.enrichment_adapter.enrich_lead(lead_data)

    async def _analyze_workflow(self, workflow_description: str) -> dict:
        """Analyze workflow via Workflow Auditor"""

        return await self.workflow_adapter.analyze_workflow(workflow_description)

    async def _generate_proposal(self, lead: Lead, workflow_data: Optional[dict]) -> dict:
        """Generate proposal via Proposal Builder"""

        lead_data = {
            "email": lead.email,
            "name": lead.name,
            "company": lead.company,
            "industry": lead.enrichment_data.get("company", {}).get("industry") if lead.enrichment_data else None,
            "company_size": lead.enrichment_data.get("company", {}).get("employee_count") if lead.enrichment_data else None,
            "pain_points": lead.enrichment_data.get("key_insights", []) if lead.enrichment_data else [],
            "goals": [],
            "notes": ""
        }

        return await self.proposal_adapter.generate_proposal(lead_data, workflow_data)

    async def health_check(self) -> dict:
        """Check health of all connected systems"""

        return {
            "lead_enrichment": await self.enrichment_adapter.health_check(),
            "workflow_auditor": await self.workflow_adapter.health_check(),
            "proposal_builder": await self.proposal_adapter.health_check()
        }
