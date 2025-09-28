import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Clock, AlertTriangle } from "lucide-react"

const metrics = [
  {
    title: "Anomalies Detected",
    value: "12.3%",
    change: "+2.1%",
    trend: "up",
    icon: TrendingUp,
    description: "vs last week",
  },
  {
    title: "Minutes Saved",
    value: "2,847",
    change: "+156",
    trend: "up",
    icon: Clock,
    description: "automation time saved",
  },
  {
    title: "Active Alerts",
    value: "23",
    change: "-5",
    trend: "down",
    icon: AlertTriangle,
    description: "requiring attention",
  },
]

export function MetricsBar() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      {metrics.map((metric, index) => (
        <Card key={index} className="bg-card border-border">
          <CardContent className="p-4 sm:p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-muted-foreground truncate">{metric.title}</p>
                <p className="text-xl sm:text-2xl font-bold text-foreground">{metric.value}</p>
                <div className="flex items-center mt-1 flex-wrap">
                  {metric.trend === "up" ? (
                    <TrendingUp className="h-4 w-4 text-green-500 mr-1 flex-shrink-0" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-green-500 mr-1 flex-shrink-0" />
                  )}
                  <span className="text-sm text-green-500 mr-1">{metric.change}</span>
                  <span className="text-xs sm:text-sm text-muted-foreground">{metric.description}</span>
                </div>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 ml-3">
                <metric.icon className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
