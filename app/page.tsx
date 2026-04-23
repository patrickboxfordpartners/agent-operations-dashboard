import { db } from "@/lib/db";
import { agentExecutions, skillExecutions, tokenUsage, systemAlerts, systemMetrics } from "@/lib/db/schema";
import { desc, eq, gte, sql } from "drizzle-orm";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export const dynamic = "force-dynamic";

async function getMetrics() {
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  // Active agents
  const activeAgents = await db
    .select()
    .from(agentExecutions)
    .where(eq(agentExecutions.status, "running"));

  // Recent executions
  const recentExecutions = await db
    .select()
    .from(agentExecutions)
    .orderBy(desc(agentExecutions.startedAt))
    .limit(10);

  // Today's stats
  const todayExecutions = await db
    .select()
    .from(agentExecutions)
    .where(gte(agentExecutions.startedAt, todayStart));

  const successCount = todayExecutions.filter((e) => e.status === "completed").length;
  const failureCount = todayExecutions.filter((e) => e.status === "failed").length;
  const successRate = todayExecutions.length > 0 ? Math.round((successCount / todayExecutions.length) * 100) : 0;

  // Token usage
  const todayTokens = await db
    .select()
    .from(tokenUsage)
    .where(gte(tokenUsage.timestamp, todayStart));

  const totalTokens = todayTokens.reduce((sum, t) => sum + t.totalTokens, 0);
  const estimatedCost = todayTokens.reduce((sum, t) => sum + (t.estimatedCost || 0), 0);

  // Active alerts
  const alerts = await db
    .select()
    .from(systemAlerts)
    .where(eq(systemAlerts.resolved, false))
    .orderBy(desc(systemAlerts.createdAt))
    .limit(5);

  // Agent type breakdown
  const agentTypes = todayExecutions.reduce((acc, e) => {
    acc[e.agentType] = (acc[e.agentType] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const agentTypeData = Object.entries(agentTypes).map(([name, value]) => ({ name, value }));

  // Average duration
  const completedToday = todayExecutions.filter((e) => e.durationMs);
  const avgDuration =
    completedToday.length > 0
      ? Math.round(completedToday.reduce((sum, e) => sum + (e.durationMs || 0), 0) / completedToday.length)
      : 0;

  return {
    activeAgents: activeAgents.length,
    totalExecutions: todayExecutions.length,
    successRate,
    totalTokens,
    estimatedCost: estimatedCost / 100, // Convert cents to dollars
    alerts: alerts.length,
    recentExecutions,
    activeAlerts: alerts,
    agentTypeData,
    avgDuration,
    successCount,
    failureCount,
  };
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

export default async function DashboardPage() {
  const metrics = await getMetrics();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Agent Operations Dashboard</h1>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Active Agents</div>
            <div className="text-3xl font-bold text-blue-600">{metrics.activeAgents}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Executions Today</div>
            <div className="text-3xl font-bold text-gray-900">{metrics.totalExecutions}</div>
            <div className="text-xs text-gray-500 mt-1">
              {metrics.successCount} success / {metrics.failureCount} failed
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Success Rate</div>
            <div className="text-3xl font-bold text-green-600">{metrics.successRate}%</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Tokens Used Today</div>
            <div className="text-3xl font-bold text-purple-600">{metrics.totalTokens.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-1">${metrics.estimatedCost.toFixed(2)} estimated</div>
          </div>
        </div>

        {/* Alerts */}
        {metrics.activeAlerts.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-red-600">⚠</span>
              Active Alerts ({metrics.activeAlerts.length})
            </h2>
            <div className="space-y-3">
              {metrics.activeAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`border-l-4 p-4 rounded ${
                    alert.severity === "critical"
                      ? "border-red-500 bg-red-50"
                      : alert.severity === "warning"
                      ? "border-yellow-500 bg-yellow-50"
                      : "border-blue-500 bg-blue-50"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-sm uppercase text-gray-600">{alert.type}</div>
                      <div className="text-gray-900 mt-1">{alert.message}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(alert.createdAt).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Agent Types */}
          {metrics.agentTypeData.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Agent Types (Today)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={metrics.agentTypeData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {metrics.agentTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Performance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Performance</h2>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-600 mb-2">Average Duration</div>
                <div className="text-2xl font-bold text-gray-900">{(metrics.avgDuration / 1000).toFixed(2)}s</div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-2">Success vs Failure</div>
                <div className="flex gap-4">
                  <div className="flex-1 bg-green-100 rounded p-3">
                    <div className="text-xs text-gray-600">Success</div>
                    <div className="text-xl font-bold text-green-600">{metrics.successCount}</div>
                  </div>
                  <div className="flex-1 bg-red-100 rounded p-3">
                    <div className="text-xs text-gray-600">Failed</div>
                    <div className="text-xl font-bold text-red-600">{metrics.failureCount}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Executions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Recent Executions</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr className="text-left text-sm text-gray-600">
                  <th className="pb-3">Agent Type</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Duration</th>
                  <th className="pb-3">Tokens</th>
                  <th className="pb-3">Started</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {metrics.recentExecutions.map((execution) => (
                  <tr key={execution.id} className="border-b last:border-0">
                    <td className="py-3 font-medium">{execution.agentType}</td>
                    <td className="py-3">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          execution.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : execution.status === "failed"
                            ? "bg-red-100 text-red-800"
                            : execution.status === "running"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {execution.status}
                      </span>
                    </td>
                    <td className="py-3 text-gray-600">
                      {execution.durationMs ? `${(execution.durationMs / 1000).toFixed(2)}s` : "-"}
                    </td>
                    <td className="py-3 text-gray-600">
                      {execution.tokensUsed ? execution.tokensUsed.toLocaleString() : "-"}
                    </td>
                    <td className="py-3 text-gray-600">{new Date(execution.startedAt).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
