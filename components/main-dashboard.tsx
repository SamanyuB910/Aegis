import { AlertsPanel } from "@/components/alerts-panel"
import { MetricsCards } from "@/components/metrics-cards"
import { TransactionFeed } from "@/components/transaction-feed"
import { FraudTrendChart } from "@/components/fraud-trend-chart"
import { MultimodalAnalysis } from "@/components/multimodal-analysis"

export function MainDashboard() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="text-center space-y-4 py-8">
        <h1 className="text-5xl font-bold text-foreground text-balance leading-tight">
          Meet your intelligent
          <span className="text-primary block">fraud detection ecosystem</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
          Get the only platform that delivers AI-powered fraud detection to supercharge the secure trade workflows and
          community.
        </p>
      </div>

      <MetricsCards />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <FraudTrendChart />
        </div>
        <div>
          <AlertsPanel />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <TransactionFeed />
        <MultimodalAnalysis />
      </div>
    </div>
  )
}
