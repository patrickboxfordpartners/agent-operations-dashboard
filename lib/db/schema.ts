import { pgTable, text, timestamp, integer, boolean, jsonb } from "drizzle-orm/pg-core";
import { createId } from "@paralleldrive/cuid2";

export const agentExecutions = pgTable("agent_executions", {
  id: text("id").primaryKey().$defaultFn(() => createId()),
  agentType: text("agent_type").notNull(),
  agentName: text("agent_name"),
  status: text("status").notNull().default("running"), // running, completed, failed, timeout
  startedAt: timestamp("started_at").notNull().defaultNow(),
  completedAt: timestamp("completed_at"),
  durationMs: integer("duration_ms"),
  tokensUsed: integer("tokens_used"),
  errorMessage: text("error_message"),
  metadata: jsonb("metadata"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const skillExecutions = pgTable("skill_executions", {
  id: text("id").primaryKey().$defaultFn(() => createId()),
  skillName: text("skill_name").notNull(),
  agentExecutionId: text("agent_execution_id").references(() => agentExecutions.id, { onDelete: "cascade" }),
  status: text("status").notNull().default("running"),
  startedAt: timestamp("started_at").notNull().defaultNow(),
  completedAt: timestamp("completed_at"),
  durationMs: integer("duration_ms"),
  errorMessage: text("error_message"),
  metadata: jsonb("metadata"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const tokenUsage = pgTable("token_usage", {
  id: text("id").primaryKey().$defaultFn(() => createId()),
  agentExecutionId: text("agent_execution_id").references(() => agentExecutions.id, { onDelete: "cascade" }),
  inputTokens: integer("input_tokens").notNull(),
  outputTokens: integer("output_tokens").notNull(),
  totalTokens: integer("total_tokens").notNull(),
  estimatedCost: integer("estimated_cost"), // in cents
  timestamp: timestamp("timestamp").notNull().defaultNow(),
});

export const systemAlerts = pgTable("system_alerts", {
  id: text("id").primaryKey().$defaultFn(() => createId()),
  type: text("type").notNull(), // agent_failure, token_threshold, timeout, error_pattern
  severity: text("severity").notNull(), // info, warning, critical
  message: text("message").notNull(),
  details: jsonb("details"),
  resolved: boolean("resolved").notNull().default(false),
  resolvedAt: timestamp("resolved_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const systemMetrics = pgTable("system_metrics", {
  id: text("id").primaryKey().$defaultFn(() => createId()),
  activeAgents: integer("active_agents").notNull(),
  queuedAgents: integer("queued_agents").notNull(),
  totalExecutionsToday: integer("total_executions_today").notNull(),
  successRate: integer("success_rate").notNull(), // percentage
  avgDurationMs: integer("avg_duration_ms").notNull(),
  tokensUsedToday: integer("tokens_used_today").notNull(),
  timestamp: timestamp("timestamp").notNull().defaultNow(),
});
