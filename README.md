# Agent Operations Dashboard

A real-time dashboard for monitoring agent activity, token usage, and system health across your AI agent infrastructure. Track execution metrics, identify bottlenecks, monitor costs, and receive alerts when issues arise.

## Features

- **Real-Time Monitoring**: Track active agents, execution status, and completion rates
- **Token Usage Tracking**: Monitor token consumption per agent with cost estimation
- **Health Alerts**: Get notified of agent failures, timeouts, and error patterns
- **Performance Metrics**: View average execution times, success rates, and throughput
- **Agent Type Analytics**: Visualize which agents are being used most frequently
- **Execution History**: Browse recent agent executions with detailed metadata
- **System Metrics**: Track overall system health, queue depth, and concurrent agents
- **Skill Execution Tracking**: Monitor which skills are called and their performance

## Quick Start

### Prerequisites

- Node.js 18+
- A Neon PostgreSQL database (or any PostgreSQL instance)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/patrickmitchellconsulting/agent-operations-dashboard.git
cd agent-operations-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Set up your environment:
```bash
cp .env.example .env
```

Edit `.env` and add your database connection string:
```
DATABASE_URL=postgresql://user:password@host:5432/database
```

4. Set up the database:
```bash
npm run db:push
```

5. Start the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Dashboard Sections

### Key Metrics

Top-level metrics displayed as cards:
- **Active Agents**: Current number of running agents
- **Executions Today**: Total agent executions with success/failure breakdown
- **Success Rate**: Percentage of successful executions
- **Tokens Used Today**: Total token consumption with estimated cost

### Active Alerts

Critical system alerts displayed prominently:
- **Agent Failures**: When agents crash or error out
- **Token Thresholds**: When usage exceeds defined limits
- **Timeouts**: When agents exceed expected execution time
- **Error Patterns**: When recurring errors are detected

### Agent Types (Pie Chart)

Visual breakdown of which agent types are being executed most frequently.

### Performance Metrics

- **Average Duration**: Mean execution time across all agents
- **Success vs Failure**: Side-by-side comparison of outcomes

### Recent Executions Table

Detailed log of recent agent executions showing:
- Agent type
- Status (running, completed, failed, timeout)
- Duration
- Token usage
- Start time

## Database Schema

### Agent Executions

```typescript
{
  id: string
  agentType: string
  agentName: string?
  status: "running" | "completed" | "failed" | "timeout"
  startedAt: timestamp
  completedAt: timestamp?
  durationMs: number?
  tokensUsed: number?
  errorMessage: string?
  metadata: json?
}
```

### Skill Executions

```typescript
{
  id: string
  skillName: string
  agentExecutionId: string
  status: "running" | "completed" | "failed"
  startedAt: timestamp
  completedAt: timestamp?
  durationMs: number?
  errorMessage: string?
  metadata: json?
}
```

### Token Usage

```typescript
{
  id: string
  agentExecutionId: string
  inputTokens: number
  outputTokens: number
  totalTokens: number
  estimatedCost: number // in cents
  timestamp: timestamp
}
```

### System Alerts

```typescript
{
  id: string
  type: "agent_failure" | "token_threshold" | "timeout" | "error_pattern"
  severity: "info" | "warning" | "critical"
  message: string
  details: json?
  resolved: boolean
  resolvedAt: timestamp?
}
```

### System Metrics

```typescript
{
  id: string
  activeAgents: number
  queuedAgents: number
  totalExecutionsToday: number
  successRate: number // percentage
  avgDurationMs: number
  tokensUsedToday: number
  timestamp: timestamp
}
```

## Integration

### Logging Agent Executions

To track agent executions in your system, insert records into the database:

```typescript
import { db } from "./lib/db";
import { agentExecutions, tokenUsage } from "./lib/db/schema";

// Start tracking
const execution = await db.insert(agentExecutions).values({
  agentType: "general-purpose",
  agentName: "code-reviewer",
  status: "running",
  startedAt: new Date(),
}).returning();

// Update on completion
await db.update(agentExecutions)
  .set({
    status: "completed",
    completedAt: new Date(),
    durationMs: 5432,
    tokensUsed: 12500,
  })
  .where(eq(agentExecutions.id, execution[0].id));

// Log token usage
await db.insert(tokenUsage).values({
  agentExecutionId: execution[0].id,
  inputTokens: 10000,
  outputTokens: 2500,
  totalTokens: 12500,
  estimatedCost: 625, // $6.25 in cents
});
```

### Creating Alerts

Trigger alerts based on conditions:

```typescript
import { systemAlerts } from "./lib/db/schema";

await db.insert(systemAlerts).values({
  type: "token_threshold",
  severity: "warning",
  message: "Token usage exceeded 80% of daily budget",
  details: { currentUsage: 80000, budget: 100000 },
  resolved: false,
});
```

## Use Cases

### Development Monitoring

Track agent performance during development to identify slow agents or high token consumption.

### Production Observability

Monitor production agent deployments for failures, timeouts, and anomalies.

### Cost Tracking

Keep tabs on token usage and estimated costs to stay within budget.

### Debugging

Review execution history and error messages to diagnose issues.

### Performance Optimization

Identify bottlenecks by analyzing average durations and failure patterns.

## Tech Stack

- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS 4**: Utility-first styling
- **Drizzle ORM**: Type-safe database queries
- **Neon PostgreSQL**: Serverless database
- **Recharts**: Data visualization library
- **@paralleldrive/cuid2**: Collision-resistant IDs

## Development

View and manage your data using Drizzle Studio:
```bash
npm run db:studio
```

Access the visual database browser at [http://localhost:4983](http://localhost:4983)

## License

MIT
