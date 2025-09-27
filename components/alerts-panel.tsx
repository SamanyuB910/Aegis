import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, Clock, Eye } from "lucide-react"

const alerts = [
  {
    id: 1,
    severity: "critical",
    title: "Unusual spending pattern detected",
    merchant: "QuickMart #247",
    amount: "$2,847.50",
    time: "2 min ago",
    confidence: 0.94,
  },
  {
    id: 2,
    severity: "high",
    title: "Receipt-transaction mismatch",
    merchant: "TechStore Online",
    amount: "$1,299.99",
    time: "8 min ago",
    confidence: 0.87,
  },
  {
    id: 3,
    severity: "medium",
    title: "Voice stress indicators",
    merchant: "FuelStop #89",
    amount: "$89.45",
    time: "15 min ago",
    confidence: 0.73,
  },
  {
    id: 4,
    severity: "high",
    title: "Merchant network anomaly",
    merchant: "Multiple locations",
    amount: "$4,567.23",
    time: "22 min ago",
    confidence: 0.91,
  },
]

const severityColors = {
  critical: "bg-destructive/10 text-destructive border-destructive/20",
  high: "bg-warning/10 text-warning border-warning/20",
  medium: "bg-primary/10 text-primary border-primary/20",
  low: "bg-muted/10 text-muted-foreground border-muted/20",
}

export function AlertsPanel() {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          <AlertTriangle className="h-5 w-5 text-destructive animate-pulse-alert" />
          Live Fraud Alerts
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {alerts.map((alert) => (
          <div key={alert.id} className="p-4 rounded-lg border bg-card/30 animate-slide-in">
            <div className="flex items-start justify-between mb-2">
              <Badge className={severityColors[alert.severity as keyof typeof severityColors]} variant="outline">
                {alert.severity.toUpperCase()}
              </Badge>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {alert.time}
              </div>
            </div>

            <h4 className="font-medium text-foreground mb-1">{alert.title}</h4>
            <p className="text-sm text-muted-foreground mb-2">
              {alert.merchant} • {alert.amount}
            </p>

            <div className="flex items-center justify-between">
              <div className="text-xs text-muted-foreground">AI Confidence: {(alert.confidence * 100).toFixed(0)}%</div>
              <Button size="sm" variant="outline" className="h-7 bg-transparent">
                <Eye className="h-3 w-3 mr-1" />
                Investigate
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
