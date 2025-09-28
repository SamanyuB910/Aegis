import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Eye, EyeOff } from "lucide-react"

const notifications = [
  {
    id: 1,
    title: "Model Updated",
    description: "Voice Agent v2.1.3 deployed",
    severity: "LOW",
    time: "2 min ago",
  },
  {
    id: 2,
    title: "High-Risk Transaction",
    description: "Card *4532 - $2,500 purchase flagged",
    severity: "HIGH",
    time: "5 min ago",
  },
  {
    id: 3,
    title: "Document Forgery",
    description: "ID verification failed - Case #FR-001",
    severity: "MED",
    time: "12 min ago",
  },
  {
    id: 4,
    title: "Voice Anomaly",
    description: "Synthetic speech detected in call",
    severity: "HIGH",
    time: "18 min ago",
  },
  {
    id: 5,
    title: "System Health",
    description: "All agents operational",
    severity: "LOW",
    time: "1 hour ago",
  },
]

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "HIGH":
      return "bg-destructive text-destructive-foreground"
    case "MED":
      return "bg-yellow-500 text-yellow-50"
    case "LOW":
      return "bg-green-500 text-green-50"
    default:
      return "bg-muted text-muted-foreground"
  }
}

export function NotificationsPanel() {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>System Events</CardTitle>
            <CardDescription>Recent alerts and notifications</CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button variant="ghost" size="icon">
              <Eye className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <EyeOff className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
          >
            <Badge className={`${getSeverityColor(notification.severity)} text-xs`}>{notification.severity}</Badge>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground">{notification.title}</p>
              <p className="text-xs text-muted-foreground">{notification.description}</p>
              <p className="text-xs text-muted-foreground mt-1">{notification.time}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
