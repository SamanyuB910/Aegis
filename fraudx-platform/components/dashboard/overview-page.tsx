import { MetricsBar } from "@/components/dashboard/metrics-bar"
import { WeeklyGraph } from "@/components/dashboard/weekly-graph"
import { NotificationsPanel } from "@/components/dashboard/notifications-panel"

export function OverviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Overview</h1>
        <p className="text-muted-foreground">Monitor fraud detection performance and system health</p>
      </div>

      <MetricsBar />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WeeklyGraph />
        </div>
        <div>
          <NotificationsPanel />
        </div>
      </div>
    </div>
  )
}
