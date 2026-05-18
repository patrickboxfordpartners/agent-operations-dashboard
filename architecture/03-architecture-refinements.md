# Architecture Refinements: Robustness & Dynamic Learning
## Making Both Systems Self-Improving and Production-Grade

---

## Critical Weaknesses in v1.0

### Second Brain Issues
❌ **No data quality validation** → Garbage in, garbage out  
❌ **No deduplication** → Same project saved 3 times with different names  
❌ **Static embeddings** → Can't adapt to new verticals/concepts  
❌ **No query feedback loop** → Don't know if retrievals were actually useful  
❌ **Rigid schema** → Adding new fields requires migration  
❌ **Cron-based pattern analysis** → Misses real-time insights  
❌ **No version control** → Can't see how projects evolved  

### Workflow Auditor Issues
❌ **No audit quality scoring** → Can't tell good audits from bad ones  
❌ **Hard-coded 3-solution template** → Sometimes 2 is enough, sometimes need 5  
❌ **No win/loss tracking** → Don't learn from rejections  
❌ **Static prompts** → Top performers can't improve the system  
❌ **No feasibility validation** → Might propose solutions that don't work  
❌ **No competitive intelligence** → Could be auditing same company twice  

---

## Refinement Strategy

We'll add **3 layers** to both systems:

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: Quality Gates (validate inputs/outputs)               │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: Feedback Loops (learn from usage)                     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: Adaptive Behavior (evolve over time)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# Part 1: Second Brain Refinements

## 1.1 Quality Gates

### Input Validation Layer

**Problem:** Bad data in → bad retrieval out. Need to catch incomplete/low-quality projects at ingestion.

**Solution:** Multi-stage validation with auto-fix attempts.

```python
from pydantic import BaseModel, validator
from typing import Optional
import anthropic

class ProjectValidation(BaseModel):
    """Enforced schema for all ingested projects"""
    
    # Required fields
    client_name: str
    vertical: str  # Must match taxonomy
    pain_point: str
    solution_description: str
    date_completed: str  # ISO 8601
    
    # Auto-extracted fields
    tools_used: list[str]
    roi_metric: Optional[str]
    cost_to_build: Optional[float]
    
    # Quality scores (generated)
    completeness_score: float  # 0-1
    reusability_score: float   # 0-1
    documentation_quality: float  # 0-1
    
    @validator('vertical')
    def validate_vertical(cls, v):
        TAXONOMY = ['healthcare', 'legal', 'manufacturing', 'retail', 'saas', 'services', 'other']
        if v.lower() not in TAXONOMY:
            raise ValueError(f"Vertical must be one of {TAXONOMY}. Got: {v}")
        return v.lower()
    
    @validator('roi_metric')
    def validate_roi(cls, v):
        if v and not any(x in v.lower() for x in ['%', 'hour', 'time', '$', 'cost', 'increase', 'reduction']):
            raise ValueError("ROI metric must include quantified improvement")
        return v

class QualityGate:
    """Validates and enriches projects before storage"""
    
    def __init__(self):
        self.claude = anthropic.Anthropic()
        self.min_completeness = 0.7
    
    async def validate_and_enrich(self, raw_project: dict) -> ProjectValidation:
        """
        1. Check completeness
        2. Attempt auto-fix if incomplete
        3. Score quality dimensions
        4. Reject if below threshold
        """
        
        # First pass: assess what's missing
        assessment = await self._assess_completeness(raw_project)
        
        if assessment['completeness_score'] < self.min_completeness:
            # Try to auto-enrich from available materials
            enriched = await self._auto_enrich(raw_project, assessment['missing_fields'])
            
            # Re-assess
            assessment = await self._assess_completeness(enriched)
            
            if assessment['completeness_score'] < self.min_completeness:
                # Still below threshold - flag for manual review
                await self._flag_for_review(raw_project, assessment)
                raise ValueError(f"Project below quality threshold: {assessment['issues']}")
        
        # Score reusability and documentation
        scores = await self._score_project(raw_project)
        
        return ProjectValidation(
            **raw_project,
            **scores
        )
    
    async def _assess_completeness(self, project: dict) -> dict:
        """Use Claude to assess what's missing"""
        
        prompt = f"""Assess this project documentation for completeness:

{json.dumps(project, indent=2)}

Return JSON:
{{
  "completeness_score": 0.0-1.0,
  "missing_fields": ["field1", "field2"],
  "issues": ["issue description"],
  "can_auto_enrich": boolean (can missing info be inferred from what's present?)
}}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    async def _auto_enrich(self, project: dict, missing_fields: list[str]) -> dict:
        """Try to fill missing fields from context"""
        
        prompt = f"""This project is missing: {missing_fields}

Can you infer these from the existing information?

Existing data:
{json.dumps(project, indent=2)}

Return the FULL project object with missing fields filled in (or null if truly unknowable).
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    async def _score_project(self, project: dict) -> dict:
        """Score reusability and documentation quality"""
        
        prompt = f"""Score this project on two dimensions (0.0-1.0):

1. **Reusability**: How applicable is this solution to other clients?
   - 1.0 = Pattern works across verticals with minimal changes
   - 0.5 = Works within same vertical with customization
   - 0.0 = Highly specific to this one client

2. **Documentation Quality**: How well-documented is the solution?
   - 1.0 = Complete architecture, prompts, lessons learned
   - 0.5 = Basic description, some details missing
   - 0.0 = Minimal info, hard to reconstruct

Project:
{json.dumps(project, indent=2)}

Return JSON: {{"reusability_score": X, "documentation_quality": Y, "reasoning": "..."}}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

### Deduplication Engine

**Problem:** Same client project might be ingested multiple times with slight variations.

**Solution:** Semantic similarity check before ingestion.

```python
class DeduplicationEngine:
    """Prevents duplicate projects from polluting the knowledge base"""
    
    def __init__(self, index: pinecone.Index, threshold: float = 0.85):
        self.index = index
        self.threshold = threshold  # Cosine similarity threshold
    
    async def check_duplicate(self, new_project: dict) -> Optional[dict]:
        """Returns existing project if duplicate found"""
        
        # Generate embedding for new project
        embedding = await self.embed(new_project['summary'])
        
        # Search for similar projects
        results = self.index.query(
            vector=embedding,
            top_k=5,
            include_metadata=True,
            filter={
                "client": new_project['client_name']  # Same client only
            }
        )
        
        for match in results['matches']:
            if match['score'] >= self.threshold:
                # Very similar - likely duplicate
                return {
                    "is_duplicate": True,
                    "existing_id": match['id'],
                    "similarity": match['score'],
                    "existing_project": match['metadata']
                }
        
        return None
    
    async def merge_or_version(self, existing: dict, new: dict) -> dict:
        """Decide whether to merge or create version"""
        
        prompt = f"""We have two similar project records for the same client:

EXISTING:
{json.dumps(existing, indent=2)}

NEW:
{json.dumps(new, indent=2)}

Are these:
A) The same project (merge - keep best info from both)
B) Different phases/versions (create v2 with link to v1)
C) Actually different projects (false positive - keep separate)

Return JSON: {{"action": "merge|version|separate", "reasoning": "...", "merged_record": {{...}} }}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        decision = json.loads(response.content[0].text)
        return decision
```

### Output Validation for Queries

**Problem:** Vector search might return irrelevant results. No way to know if query was satisfied.

**Solution:** Relevance scoring + query refinement loop.

```python
class QueryValidator:
    """Ensures retrieved results actually answer the question"""
    
    async def validate_results(self, query: str, results: list[dict], min_relevance: float = 0.7) -> dict:
        """Score how well results answer the query"""
        
        prompt = f"""User query: "{query}"

Retrieved results:
{json.dumps([r['metadata'] for r in results[:5]], indent=2)}

For each result, score relevance (0.0-1.0):
- 1.0 = Directly answers the query
- 0.5 = Partially relevant
- 0.0 = Not relevant

Also: suggest query refinement if avg relevance < 0.7

Return JSON:
{{
  "relevance_scores": [0.8, 0.6, ...],
  "avg_relevance": 0.7,
  "needs_refinement": boolean,
  "suggested_refinement": "refined query" or null
}}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        validation = json.loads(response.content[0].text)
        
        if validation['needs_refinement']:
            # Auto-retry with refined query
            return await self.retry_with_refinement(validation['suggested_refinement'])
        
        return {
            "results": results,
            "quality": validation
        }
```

---

## 1.2 Feedback Loops

### Query Usefulness Tracking

**Problem:** Don't know if retrieved solutions were actually helpful. Can't improve retrieval.

**Solution:** Implicit + explicit feedback collection.

```python
class FeedbackCollector:
    """Tracks which queries and results were actually useful"""
    
    def __init__(self):
        self.db = sqlite3.connect('brain_feedback.db')
        self._init_schema()
    
    def _init_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                query_id TEXT PRIMARY KEY,
                query TEXT,
                results TEXT,  -- JSON array of result IDs
                timestamp DATETIME,
                session_id TEXT,
                
                -- Implicit feedback
                result_clicked TEXT,  -- Which result was selected
                time_to_click_seconds FLOAT,
                follow_up_query TEXT,  -- Did they refine?
                
                -- Explicit feedback (if provided)
                usefulness_rating INTEGER,  -- 1-5 stars
                user_comment TEXT,
                
                -- Outcome tracking
                led_to_action BOOLEAN,  -- Did they build something from this?
                action_type TEXT  -- 'audit', 'proposal', 'implementation'
            )
        """)
    
    async def log_query(self, query: str, results: list, session_id: str) -> str:
        """Log query and start tracking"""
        query_id = str(uuid.uuid4())
        
        self.db.execute(
            "INSERT INTO query_logs (query_id, query, results, timestamp, session_id) VALUES (?, ?, ?, ?, ?)",
            (query_id, query, json.dumps([r['id'] for r in results]), datetime.now(), session_id)
        )
        self.db.commit()
        
        return query_id
    
    def track_result_click(self, query_id: str, result_id: str, time_to_click: float):
        """Implicit signal: user opened this result"""
        self.db.execute(
            "UPDATE query_logs SET result_clicked = ?, time_to_click_seconds = ? WHERE query_id = ?",
            (result_id, time_to_click, query_id)
        )
        self.db.commit()
    
    def track_follow_up(self, query_id: str, new_query: str):
        """Implicit signal: query wasn't satisfied, user refined it"""
        self.db.execute(
            "UPDATE query_logs SET follow_up_query = ? WHERE query_id = ?",
            (new_query, query_id)
        )
        self.db.commit()
    
    async def analyze_query_patterns(self) -> dict:
        """Find patterns in successful vs unsuccessful queries"""
        
        # Get queries that led to action vs those that didn't
        successful = self.db.execute("""
            SELECT query, results, result_clicked 
            FROM query_logs 
            WHERE led_to_action = 1
        """).fetchall()
        
        unsuccessful = self.db.execute("""
            SELECT query, results, follow_up_query 
            FROM query_logs 
            WHERE follow_up_query IS NOT NULL AND led_to_action = 0
        """).fetchall()
        
        # Use Claude to identify patterns
        prompt = f"""Analyze query patterns to improve retrieval:

SUCCESSFUL queries (led to action):
{json.dumps(successful, indent=2)}

UNSUCCESSFUL queries (had to refine):
{json.dumps(unsuccessful, indent=2)}

Identify:
1. What makes a query successful? (patterns in phrasing, specificity)
2. Common failure modes (what questions can't we answer well?)
3. Suggested improvements to embedding strategy or query rewriting
4. Knowledge gaps (what project types should we prioritize capturing?)

Return JSON with actionable insights.
"""
        
        response = await self.claude.messages.create(
            model="claude-opus-4-7",  # Use Opus for strategic analysis
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

### Embedding Quality Monitoring

**Problem:** Embedding models can have "blind spots" for domain-specific terminology.

**Solution:** Track retrieval performance and fine-tune embeddings.

```python
class EmbeddingMonitor:
    """Monitors and improves embedding quality over time"""
    
    def __init__(self):
        self.voyage = voyageai.Client()
        self.metrics_db = {}
    
    async def evaluate_embedding_quality(self) -> dict:
        """Run benchmark queries to assess retrieval quality"""
        
        # Define golden test cases
        test_cases = [
            {
                "query": "dental scheduling automation",
                "expected_results": ["proj_smilecare_scheduling", "proj_dental_intake"],
                "vertical": "healthcare"
            },
            {
                "query": "reduce manual data entry for law firms",
                "expected_results": ["proj_legal_intake", "proj_boutiquelaw_crm"],
                "vertical": "legal"
            }
            # Add more as you build
        ]
        
        results = []
        for test in test_cases:
            retrieved = await brain.search(test['query'], vertical=test['vertical'], limit=10)
            retrieved_ids = [r['id'] for r in retrieved]
            
            # Calculate recall: how many expected results were in top 10?
            recall = len(set(test['expected_results']) & set(retrieved_ids)) / len(test['expected_results'])
            
            # Calculate MRR (Mean Reciprocal Rank): position of first relevant result
            first_relevant_pos = None
            for i, rid in enumerate(retrieved_ids):
                if rid in test['expected_results']:
                    first_relevant_pos = i + 1
                    break
            
            mrr = 1.0 / first_relevant_pos if first_relevant_pos else 0.0
            
            results.append({
                "query": test['query'],
                "recall": recall,
                "mrr": mrr,
                "retrieved": retrieved_ids[:3]
            })
        
        avg_recall = sum(r['recall'] for r in results) / len(results)
        avg_mrr = sum(r['mrr'] for r in results) / len(results)
        
        return {
            "avg_recall": avg_recall,
            "avg_mrr": avg_mrr,
            "details": results,
            "recommendation": "Fine-tune embeddings" if avg_recall < 0.7 else "Performance good"
        }
    
    async def fine_tune_embeddings(self, training_data: list[dict]):
        """
        If Voyage quality drops, fine-tune on your domain
        (Voyage AI supports custom fine-tuning)
        """
        
        # Format training data: (query, positive_doc, negative_doc) triplets
        triplets = []
        for item in training_data:
            triplets.append({
                "query": item['query'],
                "positive": item['clicked_result'],
                "negative": item['ignored_results'][0]  # Lowest-ranked result
            })
        
        # Submit fine-tuning job
        job = self.voyage.finetune.create(
            model="voyage-2",
            training_data=triplets,
            name="second-brain-custom"
        )
        
        return job.id
```

---

## 1.3 Adaptive Behavior

### Dynamic Schema Evolution

**Problem:** Hard-coded schema doesn't adapt as you enter new verticals or solution types.

**Solution:** Schema-less core + dynamic field detection.

```python
class DynamicSchema:
    """Learns new fields and patterns over time"""
    
    def __init__(self):
        self.field_registry = self._load_field_registry()
        self.claude = anthropic.Anthropic()
    
    def _load_field_registry(self) -> dict:
        """Load known fields and their distributions"""
        return {
            "core_fields": ["client_name", "vertical", "pain_point", "solution_description"],
            "optional_fields": {
                "roi_metric": {"frequency": 0.85, "importance": "high"},
                "tools_used": {"frequency": 0.95, "importance": "high"},
                "cost_to_build": {"frequency": 0.60, "importance": "medium"},
                "client_satisfaction": {"frequency": 0.40, "importance": "low"}
            },
            "emerging_fields": {}  # Fields appearing in recent projects
        }
    
    async def detect_new_fields(self, recent_projects: list[dict]) -> list[str]:
        """Find fields that are appearing consistently in new projects"""
        
        # Extract all fields from recent projects
        field_counts = {}
        for proj in recent_projects[-20:]:  # Last 20 projects
            for field in proj.keys():
                if field not in self.field_registry['core_fields']:
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        # Fields appearing in >30% of recent projects might be important
        emerging = {
            field: count/20 
            for field, count in field_counts.items() 
            if count/20 > 0.3 and field not in self.field_registry['optional_fields']
        }
        
        if emerging:
            # Ask Claude if these should be promoted
            prompt = f"""I'm seeing these new fields in recent projects:

{json.dumps(emerging, indent=2)}

Should any of these be promoted to standard fields in our schema?
Consider: frequency, information value, reusability

Return JSON:
{{
  "promote": ["field1", "field2"],
  "reasoning": {{"field1": "why it's useful", ...}},
  "importance": {{"field1": "high|medium|low", ...}}
}}
"""
            
            response = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = json.loads(response.content[0].text)
            
            # Update registry
            for field in decision['promote']:
                self.field_registry['optional_fields'][field] = {
                    "frequency": emerging[field],
                    "importance": decision['importance'][field],
                    "added": datetime.now().isoformat()
                }
            
            self._save_field_registry()
        
        return list(emerging.keys())
```

### Self-Improving Pattern Recognition

**Problem:** Pattern analyzer is static - doesn't get better at finding productizable opportunities.

**Solution:** Track which pattern suggestions led to revenue.

```python
class AdaptivePatternAnalyzer:
    """Pattern analyzer that learns from outcomes"""
    
    def __init__(self):
        self.pattern_history = self._load_pattern_history()
        self.claude = anthropic.Anthropic()
    
    async def analyze_with_context(self, projects: list[dict]) -> dict:
        """Pattern analysis that considers past success rates"""
        
        # Get historical performance of past suggestions
        past_performance = self._get_pattern_performance()
        
        prompt = f"""Analyze these projects for productizable patterns:

PROJECTS:
{json.dumps(projects, indent=2)}

HISTORICAL CONTEXT (past pattern suggestions and outcomes):
{json.dumps(past_performance, indent=2)}

Learn from history:
- Patterns marked "high_revenue" should inform your current analysis
- Patterns marked "no_traction" might not be as good as they seemed
- Look for similar patterns to successful ones

Return top 3 product opportunities with:
- Confidence score (0-1) based on historical precedent
- Similar past patterns (reference IDs)
- Market validation evidence
"""
        
        response = await self.claude.messages.create(
            model="claude-opus-4-7",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        patterns = json.loads(response.content[0].text)
        
        # Log for future learning
        pattern_id = self._save_pattern_suggestion(patterns)
        
        return {
            "patterns": patterns,
            "tracking_id": pattern_id
        }
    
    def update_pattern_outcome(self, pattern_id: str, outcome: dict):
        """Called when you know if a pattern suggestion led to business"""
        
        self.pattern_history[pattern_id]['outcome'] = {
            "revenue_generated": outcome.get('revenue', 0),
            "clients_closed": outcome.get('clients', 0),
            "time_to_first_deal": outcome.get('days_to_deal', None),
            "status": "high_revenue" if outcome.get('revenue', 0) > 10000 else "low_revenue"
        }
        
        self._save_pattern_history()
```

---

# Part 2: Workflow Auditor Refinements

## 2.1 Quality Gates

### Audit Output Validation

**Problem:** Generated audits might have hallucinated tools, wrong ROI math, or unfeasible architectures.

**Solution:** Multi-stage validation before client sees it.

```python
class AuditValidator:
    """Validates audit outputs before delivery"""
    
    async def validate_audit(self, audit: dict) -> dict:
        """Run checks on generated audit"""
        
        checks = await asyncio.gather(
            self._validate_tools_exist(audit['solutions']),
            self._validate_roi_math(audit['workflow'], audit['solutions']),
            self._validate_technical_feasibility(audit['solutions']),
            self._check_cost_estimates(audit['solutions'])
        )
        
        tool_check, roi_check, feasibility_check, cost_check = checks
        
        issues = []
        if not tool_check['valid']:
            issues.extend(tool_check['issues'])
        if not roi_check['valid']:
            issues.extend(roi_check['issues'])
        if not feasibility_check['valid']:
            issues.extend(feasibility_check['issues'])
        if not cost_check['valid']:
            issues.extend(cost_check['issues'])
        
        if issues:
            # Auto-fix or flag for review
            fixed_audit = await self._auto_fix_issues(audit, issues)
            return fixed_audit
        
        return audit
    
    async def _validate_tools_exist(self, solutions: dict) -> dict:
        """Check that mentioned tools are real and have the APIs claimed"""
        
        all_tools = []
        for solution in solutions.values():
            if isinstance(solution, dict) and 'tools' in solution:
                all_tools.extend(solution['tools'])
        
        # Query tool knowledge base
        validations = []
        for tool in set(all_tools):
            exists = await self._check_tool_exists(tool)
            validations.append({
                "tool": tool,
                "exists": exists,
                "alternatives": await self._get_alternatives(tool) if not exists else None
            })
        
        invalid = [v for v in validations if not v['exists']]
        
        return {
            "valid": len(invalid) == 0,
            "issues": [f"Tool '{v['tool']}' doesn't exist or doesn't have claimed capabilities. Consider: {v['alternatives']}" for v in invalid]
        }
    
    async def _validate_roi_math(self, workflow: dict, solutions: dict) -> dict:
        """Verify ROI calculations are arithmetically correct"""
        
        issues = []
        
        for solution_key, solution in solutions.items():
            if not isinstance(solution, dict):
                continue
                
            current_annual = workflow['current_cost']['annual_cost']
            projected_annual = solution['estimated_outcomes']['annual_cost_after']
            claimed_savings = solution['estimated_outcomes']['annual_savings']
            
            actual_savings = current_annual - projected_annual
            
            if abs(actual_savings - claimed_savings) > 100:  # Allow $100 rounding
                issues.append(f"{solution_key}: ROI math error. Claimed ${claimed_savings} savings but should be ${actual_savings}")
            
            # Check payback calculation
            build_cost = solution['build_cost']['total']
            monthly_savings = claimed_savings / 12
            claimed_payback = solution['build_cost']['payback_months']
            actual_payback = build_cost / monthly_savings
            
            if abs(actual_payback - claimed_payback) > 0.5:
                issues.append(f"{solution_key}: Payback period error. Claimed {claimed_payback}mo but should be {actual_payback:.1f}mo")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    async def _validate_technical_feasibility(self, solutions: dict) -> dict:
        """Use Claude + Second Brain to check if architectures are buildable"""
        
        prompt = f"""Review these solution architectures for technical feasibility:

{json.dumps(solutions, indent=2)}

For each solution, assess:
1. Are the integrations actually possible with the tools listed?
2. Is the timeline realistic for the described scope?
3. Are there obvious technical blockers not mentioned?

Return JSON:
{{
  "solution_1_conservative": {{"feasible": true/false, "issues": ["..."], "suggestions": ["..."]}},
  ...
}}
"""
        
        # Query Second Brain for similar solutions
        similar = await brain.search("similar architectures", limit=5)
        prompt += f"\n\nSimilar proven solutions:\n{json.dumps(similar, indent=2)}"
        
        response = await self.claude.messages.create(
            model="claude-opus-4-7",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        assessment = json.loads(response.content[0].text)
        
        issues = []
        for solution, result in assessment.items():
            if not result['feasible']:
                issues.append(f"{solution}: {', '.join(result['issues'])}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": assessment
        }
```

### Input Quality Scoring

**Problem:** Bad input (vague Loom, incomplete doc) → bad audit. Catch this early.

**Solution:** Score input quality and request clarification if needed.

```python
class InputQualityScorer:
    """Assesses whether we have enough info to generate a good audit"""
    
    async def score_input(self, audit_input: dict) -> dict:
        """Score input quality before processing"""
        
        prompt = f"""Assess this workflow description for completeness:

{audit_input['transcript'] if 'transcript' in audit_input else audit_input['text']}

Score these dimensions (0-1):
1. **Clarity**: Is the workflow clearly described step-by-step?
2. **Quantification**: Are there time/cost/frequency metrics?
3. **Context**: Do we know company size, vertical, current tools?
4. **Pain points**: Are frustrations explicitly stated?
5. **Completeness**: Any obvious gaps in the process description?

Return JSON:
{{
  "scores": {{"clarity": X, "quantification": X, ...}},
  "overall_score": X,
  "missing_info": ["What's missing"],
  "clarifying_questions": ["Questions to ask client"],
  "can_proceed": boolean (true if overall > 0.6)
}}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        assessment = json.loads(response.content[0].text)
        
        if not assessment['can_proceed']:
            # Send clarifying questions to client
            await self._request_clarification(audit_input, assessment['clarifying_questions'])
        
        return assessment
```

---

## 2.2 Feedback Loops

### Win/Loss Analysis

**Problem:** Don't know why audits convert (or don't). Can't improve.

**Solution:** Track outcomes and learn from patterns.

```python
class OutcomeTracker:
    """Tracks what happens after audits are delivered"""
    
    def __init__(self):
        self.db = sqlite3.connect('audit_outcomes.db')
        self._init_schema()
    
    def _init_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS audit_outcomes (
                audit_id TEXT PRIMARY KEY,
                client_name TEXT,
                vertical TEXT,
                delivered_at DATETIME,
                
                -- Engagement metrics
                page_views INTEGER,
                time_on_page_seconds INTEGER,
                clicked_solution TEXT,  -- Which solution they explored
                
                -- Outcome
                outcome TEXT,  -- 'accepted', 'rejected', 'ghosted', 'negotiating'
                outcome_date DATETIME,
                solution_chosen TEXT,  -- conservative/balanced/aggressive
                deal_value FLOAT,
                close_reason TEXT,  -- Why they accepted/rejected
                
                -- Audit characteristics
                audit_quality_score FLOAT,
                roi_range_low FLOAT,
                roi_range_high FLOAT,
                num_solutions_offered INTEGER,
                custom_recommendations BOOLEAN
            )
        """)
    
    async def analyze_conversion_patterns(self) -> dict:
        """Find what makes audits convert"""
        
        wins = self.db.execute("""
            SELECT * FROM audit_outcomes 
            WHERE outcome = 'accepted'
        """).fetchall()
        
        losses = self.db.execute("""
            SELECT * FROM audit_outcomes 
            WHERE outcome = 'rejected'
        """).fetchall()
        
        prompt = f"""Analyze win/loss patterns:

WINS (n={len(wins)}):
{json.dumps(wins, indent=2)}

LOSSES (n={len(losses)}):
{json.dumps(losses, indent=2)}

Identify:
1. What characteristics do winning audits share?
2. Common reasons for rejection?
3. Which solution type (conservative/balanced/aggressive) wins most often?
4. Does ROI range correlate with close rate?
5. Vertical-specific patterns?
6. Optimal page engagement (too short = didn't read, too long = confused?)

Return actionable insights to improve future audits.
"""
        
        response = await self.claude.messages.create(
            model="claude-opus-4-7",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        insights = json.loads(response.content[0].text)
        
        # Update audit generation prompts based on insights
        await self._update_generation_strategy(insights)
        
        return insights
    
    async def _update_generation_strategy(self, insights: dict):
        """Modify audit generation based on learnings"""
        
        # Example: if balanced solutions win 80% of the time, 
        # make that the default recommendation
        
        if insights.get('best_solution_type'):
            config.set('default_recommendation', insights['best_solution_type'])
        
        # Example: if high ROI (>5x) scares people off,
        # cap recommendations at 4x
        
        if insights.get('optimal_roi_range'):
            config.set('roi_cap', insights['optimal_roi_range']['max'])
```

### A/B Testing for Solution Generation

**Problem:** Don't know if different prompt strategies produce better audits.

**Solution:** Randomly vary prompts and track which convert better.

```python
class AuditABTester:
    """Tests different audit generation strategies"""
    
    def __init__(self):
        self.variants = {
            "control": {
                "system_prompt": STANDARD_SYSTEM_PROMPT,
                "solution_count": 3,
                "detail_level": "medium"
            },
            "variant_a_concise": {
                "system_prompt": STANDARD_SYSTEM_PROMPT + "\n\nBe extremely concise. Busy executives prefer brevity.",
                "solution_count": 3,
                "detail_level": "low"
            },
            "variant_b_detailed": {
                "system_prompt": STANDARD_SYSTEM_PROMPT + "\n\nProvide extensive detail. Assume technical buyer.",
                "solution_count": 3,
                "detail_level": "high"
            },
            "variant_c_two_solutions": {
                "system_prompt": STANDARD_SYSTEM_PROMPT + "\n\nOnly offer 2 solutions: conservative and aggressive.",
                "solution_count": 2,
                "detail_level": "medium"
            }
        }
        self.assignment_db = {}
    
    def assign_variant(self, audit_id: str) -> str:
        """Randomly assign audit to a variant"""
        variant = random.choice(list(self.variants.keys()))
        self.assignment_db[audit_id] = variant
        return variant
    
    def get_variant_config(self, variant: str) -> dict:
        return self.variants[variant]
    
    async def analyze_test_results(self) -> dict:
        """Calculate which variant performs best"""
        
        results = {}
        for variant in self.variants.keys():
            audits = [aid for aid, v in self.assignment_db.items() if v == variant]
            outcomes = outcome_tracker.get_outcomes(audits)
            
            results[variant] = {
                "n": len(audits),
                "conversion_rate": sum(1 for o in outcomes if o['outcome'] == 'accepted') / len(audits) if audits else 0,
                "avg_deal_value": np.mean([o['deal_value'] for o in outcomes if o['outcome'] == 'accepted']) if any(o['outcome'] == 'accepted' for o in outcomes) else 0,
                "avg_time_to_close": np.mean([o['days_to_close'] for o in outcomes if o['outcome'] == 'accepted']) if any(o['outcome'] == 'accepted' for o in outcomes) else 0
            }
        
        # Statistical significance test
        winner = max(results.items(), key=lambda x: x[1]['conversion_rate'])
        
        return {
            "results": results,
            "winner": winner[0],
            "significant": self._is_significant(results),
            "recommendation": "Deploy winner" if self._is_significant(results) else "Keep testing"
        }
```

---

## 2.3 Adaptive Behavior

### Dynamic Solution Count

**Problem:** Always generating 3 solutions is arbitrary. Sometimes 2 is right, sometimes 4.

**Solution:** Decide dynamically based on workflow complexity.

```python
class AdaptiveSolutionGenerator:
    """Determines optimal number of solutions per audit"""
    
    async def decide_solution_count(self, workflow: dict) -> int:
        """Decide how many solutions to generate"""
        
        prompt = f"""Analyze this workflow to determine optimal solution count:

{json.dumps(workflow, indent=2)}

Factors:
- Complexity: Simple workflows (3-5 steps) → 2 solutions might be enough
- Ambiguity: If requirements are vague → offer more options (4-5)
- Risk tolerance: Can we infer from company size/vertical?
- Budget constraints: Are there signals about budget sensitivity?

Return JSON:
{{
  "solution_count": 2-5,
  "reasoning": "...",
  "solution_types": ["conservative", "balanced", ...],
  "skip_aggressive": boolean (if it's overkill)
}}
"""
        
        response = await self.claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        decision = json.loads(response.content[0].text)
        return decision
```

### Context-Aware Prompt Engineering

**Problem:** Same prompt for all verticals. Healthcare needs different framing than retail.

**Solution:** Dynamic prompt construction based on vertical + past wins.

```python
class ContextualPromptBuilder:
    """Builds prompts tailored to vertical and client context"""
    
    def __init__(self):
        self.vertical_contexts = self._load_vertical_contexts()
    
    def _load_vertical_contexts(self) -> dict:
        """Load vertical-specific insights from past wins"""
        return {
            "healthcare": {
                "common_pains": ["HIPAA compliance", "manual scheduling", "patient communication"],
                "preferred_tools": ["Make.com over Zapier (IT approval easier)", "Claude over OpenAI (data residency)"],
                "decision_makers": ["Practice manager", "Office administrator"],
                "buying_cycle": "2-4 weeks",
                "objections": ["Security concerns", "Staff adoption"],
                "winning_frames": ["Time savings for patient care", "Reduce burnout"]
            },
            "legal": {
                "common_pains": ["Client intake", "Document review", "Billing"],
                "preferred_tools": ["Clio integration required", "DocuSign"],
                "decision_makers": ["Managing partner", "Office manager"],
                "buying_cycle": "4-8 weeks",
                "objections": ["Client confidentiality", "Bar association rules"],
                "winning_frames": ["More billable hours", "Competitive advantage"]
            }
            # Add more as you learn
        }
    
    async def build_prompt(self, workflow: dict, client: dict) -> str:
        """Construct prompt with vertical-specific context"""
        
        vertical = client['vertical']
        context = self.vertical_contexts.get(vertical, {})
        
        # Base prompt
        prompt = STANDARD_SYSTEM_PROMPT
        
        # Add vertical context
        if context:
            prompt += f"""

VERTICAL-SPECIFIC CONTEXT ({vertical.upper()}):
- Common pain points in this industry: {context.get('common_pains', [])}
- Tool preferences: {context.get('preferred_tools', [])}
- Typical decision makers: {context.get('decision_makers', [])}
- Buying cycle: {context.get('buying_cycle', 'unknown')}
- Common objections: {context.get('objections', [])}
- Frames that win: {context.get('winning_frames', [])}

ADAPT YOUR RECOMMENDATIONS to these patterns. Use proven tools for this vertical.
Address likely objections preemptively. Frame ROI in terms that resonate.
"""
        
        # Add similar past wins
        similar_wins = await self._get_similar_wins(vertical, workflow['workflow_name'])
        if similar_wins:
            prompt += f"""

SIMILAR SUCCESSFUL PROJECTS:
{json.dumps(similar_wins, indent=2)}

Reference these as social proof in your recommendations.
"""
        
        return prompt
    
    async def update_vertical_context(self, vertical: str, new_learnings: dict):
        """Update context when we learn something new about a vertical"""
        
        if vertical not in self.vertical_contexts:
            self.vertical_contexts[vertical] = {}
        
        for key, value in new_learnings.items():
            if key in self.vertical_contexts[vertical]:
                # Merge with existing
                if isinstance(value, list):
                    self.vertical_contexts[vertical][key].extend(value)
                    # Deduplicate
                    self.vertical_contexts[vertical][key] = list(set(self.vertical_contexts[vertical][key]))
            else:
                self.vertical_contexts[vertical][key] = value
        
        self._save_vertical_contexts()
```

### Self-Optimizing ROI Calibration

**Problem:** ROI estimates might be too optimistic or conservative. Need to calibrate based on reality.

**Solution:** Track actual vs. estimated ROI and adjust.

```python
class ROICalibrator:
    """Adjusts ROI estimates based on actual outcomes"""
    
    def __init__(self):
        self.calibration_db = self._load_calibration_data()
    
    async def calibrate_estimate(self, raw_estimate: dict) -> dict:
        """Apply correction factors based on historical accuracy"""
        
        vertical = raw_estimate['vertical']
        solution_type = raw_estimate['solution_type']
        
        # Get historical accuracy for this vertical + solution type
        history = self.calibration_db.get(f"{vertical}_{solution_type}", [])
        
        if len(history) < 5:
            # Not enough data, return raw estimate with uncertainty flag
            return {
                **raw_estimate,
                "confidence": "low",
                "note": "Estimate not yet calibrated for this vertical/solution combination"
            }
        
        # Calculate average variance
        actual_to_estimated = [h['actual_roi'] / h['estimated_roi'] for h in history]
        avg_multiplier = np.mean(actual_to_estimated)
        
        # Apply correction
        calibrated = {
            **raw_estimate,
            "original_annual_savings": raw_estimate['annual_savings'],
            "calibrated_annual_savings": raw_estimate['annual_savings'] * avg_multiplier,
            "confidence": "high" if len(history) > 20 else "medium",
            "historical_accuracy": f"Past estimates were {(avg_multiplier - 1) * 100:.0f}% {'high' if avg_multiplier < 1 else 'low'}",
            "sample_size": len(history)
        }
        
        return calibrated
    
    def record_actual_roi(self, audit_id: str, actual_outcomes: dict):
        """Called 3-6 months after implementation to record actual ROI"""
        
        original_estimate = self._get_original_estimate(audit_id)
        
        self.calibration_db[f"{original_estimate['vertical']}_{original_estimate['solution_type']}"].append({
            "audit_id": audit_id,
            "estimated_roi": original_estimate['annual_savings'],
            "actual_roi": actual_outcomes['measured_savings'],
            "variance": actual_outcomes['measured_savings'] / original_estimate['annual_savings'],
            "recorded_at": datetime.now().isoformat()
        })
        
        self._save_calibration_data()
```

---

## 1.4 & 2.4: System-Wide Resilience

### Graceful Degradation

**Problem:** If Claude API is down, entire system fails.

**Solution:** Fallback strategies.

```python
class ResilientAIService:
    """Wraps Claude API with fallbacks"""
    
    def __init__(self):
        self.primary = anthropic.Anthropic()
        self.cache = RedisCache()
        self.fallback_enabled = True
    
    async def complete(self, prompt: str, model: str = "claude-sonnet-4-6", **kwargs):
        """Try primary, fall back to cache or degraded mode"""
        
        # Check cache first
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        if cached := await self.cache.get(cache_key):
            return {"content": cached, "source": "cache"}
        
        try:
            # Try primary service
            response = await self.primary.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=30.0,
                **kwargs
            )
            
            # Cache successful response
            await self.cache.set(cache_key, response.content[0].text, expire=3600)
            
            return {"content": response.content[0].text, "source": "claude"}
        
        except anthropic.APIError as e:
            if self.fallback_enabled:
                return await self._fallback_strategy(prompt, model)
            else:
                raise
    
    async def _fallback_strategy(self, prompt: str, model: str):
        """What to do when Claude is unavailable"""
        
        # Option 1: Use cached similar response
        similar = await self.cache.get_similar(prompt, threshold=0.8)
        if similar:
            return {
                "content": similar,
                "source": "cache_similar",
                "warning": "Using similar cached response (Claude unavailable)"
            }
        
        # Option 2: Return template-based response
        if "extract_workflow" in prompt:
            return {
                "content": json.dumps(TEMPLATE_WORKFLOW),
                "source": "template",
                "warning": "Using template (Claude unavailable) - manual review required"
            }
        
        # Option 3: Fail gracefully with clear message
        raise ServiceUnavailableError("AI service temporarily unavailable. Your request has been queued for manual processing.")
```

### Rate Limiting & Cost Controls

**Problem:** Runaway costs if something goes wrong.

**Solution:** Hard limits + alerting.

```python
class CostGovernor:
    """Prevents runaway AI spend"""
    
    def __init__(self, daily_limit: float = 100.0):
        self.daily_limit = daily_limit
        self.current_spend = 0.0
        self.reset_date = datetime.now().date()
    
    async def check_budget(self, estimated_cost: float) -> bool:
        """Returns False if this request would exceed budget"""
        
        # Reset counter if new day
        if datetime.now().date() > self.reset_date:
            self.current_spend = 0.0
            self.reset_date = datetime.now().date()
        
        if self.current_spend + estimated_cost > self.daily_limit:
            await self._alert_budget_exceeded()
            return False
        
        return True
    
    def record_spend(self, actual_cost: float):
        """Log actual spend"""
        self.current_spend += actual_cost
        
        # Alert at thresholds
        if self.current_spend > self.daily_limit * 0.8:
            asyncio.create_task(self._alert_approaching_limit())
    
    async def _alert_budget_exceeded(self):
        """Send notification that budget is exhausted"""
        await send_notification(
            channel="slack",
            message=f"🚨 Daily AI budget exceeded: ${self.current_spend:.2f} / ${self.daily_limit:.2f}. Further requests will be queued."
        )
```

---

## Performance Monitoring Dashboard

Both systems should report health metrics:

```python
class SystemHealth:
    """Unified health monitoring"""
    
    async def get_health(self) -> dict:
        return {
            "second_brain": {
                "vector_count": await brain.index.describe_index_stats(),
                "avg_query_latency_ms": await brain.get_avg_latency(),
                "last_ingestion": await brain.get_last_ingestion_time(),
                "quality_score": await brain.get_avg_completeness_score(),
                "cache_hit_rate": await brain.get_cache_hit_rate()
            },
            "workflow_auditor": {
                "audits_delivered_today": await auditor.count_today(),
                "avg_generation_time_seconds": await auditor.get_avg_time(),
                "conversion_rate_7d": await auditor.get_conversion_rate(days=7),
                "pending_reviews": await auditor.count_pending(),
                "api_health": await auditor.check_dependencies()
            },
            "cost_tracking": {
                "spend_today": cost_governor.current_spend,
                "budget_remaining": cost_governor.daily_limit - cost_governor.current_spend,
                "burn_rate": await cost_tracker.get_hourly_rate()
            }
        }
```

---

## Next Steps: Incremental Implementation

Don't build all of this at once. Prioritize:

### Week 1-2: Quality Gates (Foundational)
- Input/output validation
- Deduplication
- ROI math checking

### Week 3-4: Feedback Loops (Compound value)
- Query tracking
- Win/loss analysis
- Outcome logging

### Week 5-6: Adaptive Behavior (Long-term improvement)
- Dynamic schema
- A/B testing
- Self-calibration

### Ongoing: Resilience (As needed)
- Add fallbacks when you hit issues
- Set cost limits before first production use
- Monitor and alert from day 1

Want me to now generate the **starter code** with these refinements baked in?
