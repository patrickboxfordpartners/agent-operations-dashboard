"""Main audit orchestrator"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "second-brain"))

from shared.models import AuditInput, AuditOutput
from processing.workflow_extractor import extractor
from processing.solution_generator import generator

# Import Second Brain for similar solutions
try:
    from query.search import brain_search
    SECOND_BRAIN_AVAILABLE = True
except ImportError:
    SECOND_BRAIN_AVAILABLE = False
    print("⚠️  Second Brain not available - audits will work but won't reference past projects")

class WorkflowAuditor:
    """Orchestrates the full audit pipeline"""

    async def generate_audit(self, audit_input: AuditInput) -> AuditOutput:
        """
        Main audit generation pipeline

        Steps:
        1. Extract structured workflow
        2. Query Second Brain for similar solutions
        3. Generate 3 automation solutions
        4. Package as AuditOutput

        Args:
            audit_input: Client workflow description

        Returns:
            Complete audit with solutions
        """

        print(f"📊 Generating audit for {audit_input.client.name}...")

        # Step 1: Extract workflow structure
        print("  ⚙️  Extracting workflow structure...")
        workflow = await extractor.extract(
            content=audit_input.content,
            client_name=audit_input.client.name,
            vertical=audit_input.client.vertical
        )
        print(f"  ✅ Found {len(workflow.steps)} steps")

        # Step 2: Find similar solutions
        similar_solutions = []
        if SECOND_BRAIN_AVAILABLE:
            print("  🔍 Searching Second Brain for similar solutions...")
            try:
                similar = await brain_search.search(
                    query=workflow.workflow_name,
                    vertical=audit_input.client.vertical,
                    limit=3
                )
                similar_solutions = similar
                print(f"  ✅ Found {len(similar_solutions)} similar projects")
            except Exception as e:
                print(f"  ⚠️  Second Brain search failed: {e}")

        # Step 3: Generate solutions
        print("  💡 Generating automation solutions...")
        solutions = await generator.generate(
            workflow=workflow,
            vertical=audit_input.client.vertical,
            similar_solutions=similar_solutions
        )
        print(f"  ✅ Generated {len(solutions)-2} solutions")  # -2 for recommended_solution and reasoning keys

        # Step 4: Package output
        # Extract only the Solution objects (not the metadata keys)
        solution_objects = {
            k: v for k, v in solutions.items()
            if k.startswith('solution_')
        }

        audit_output = AuditOutput(
            audit_id=audit_input.audit_id,
            client_name=audit_input.client.name,
            vertical=audit_input.client.vertical,
            workflow=workflow,
            solutions=solution_objects,
            recommended_solution=solutions.get('recommended_solution', 'solution_2_balanced')
        )

        print(f"✅ Audit complete for {audit_input.client.name}")

        return audit_output

# Singleton
auditor = WorkflowAuditor()
