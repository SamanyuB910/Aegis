import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, DollarSign, Shield, TrendingUp, TrendingDown } from "lucide-react"

const metrics = [
  {
    title: "Total Transactions",
    value: "2,847,392",
    change: "+12.5%",
    trend: "up",
    icon: TrendingUp,
    color: "text-primary",
  },
  {
    title: "Fraud Cases Detected",
    value: "1,247",
    change: "+8.2%",
    trend: "up",
    icon: AlertTriangle,
    color: "text-destructive",
  },
  {
    title: "Money Saved",
    value: "$2.4M",
    change: "+15.3%",
    trend: "up",
    icon: DollarSign,
    color: "text-success",
  },
  {
    title: "False Positive Rate",
    value: "2.1%",
    change: "-0.8%",
    trend: "down",
    icon: Shield,
    color: "text-warning",
  },
]

export function MetricsCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {metrics.map((metric) => (
        <Card key={metric.title} className="card-hover bg-card border-0 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-sm font-medium text-card-foreground/70">{metric.title}</CardTitle>
            <div className="p-2 rounded-full bg-primary/10">
              <metric.icon className={`h-5 w-5 ${metric.color}`} />
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-3xl font-bold text-card-foreground">{metric.value}</div>
            <div className="flex items-center gap-2">
              <Badge
                variant={metric.trend === "up" ? "default" : "secondary"}
                className={
                  metric.trend === "up"
                    ? "bg-primary text-primary-foreground font-medium"
                    : "bg-secondary text-secondary-foreground font-medium"
                }
              >
                {metric.trend === "up" ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {metric.change}
              </Badge>
              <span className="text-sm text-card-foreground/60">vs last month</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
