"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { X, Settings, RefreshCw, AlertTriangle, CheckCircle, Clock, TrendingUp } from "lucide-react"

interface AgentDetailsProps {
  agent: any
  onClose: () => void
}

export function AgentDetails({ agent, onClose }: AgentDetailsProps) {
  const getHealthColor = (status: string) => {
    switch (status) {
      case "OK":
        return "bg-green-500 text-green-50"
      case "Warning":
        return "bg-yellow-500 text-yellow-50"
      case "Offline":
        return "bg-destructive text-destructive-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const getHealthIcon = (status: string) => {
    switch (status) {
      case "OK":
        return CheckCircle
      case "Warning":
        return AlertTriangle
      case "Offline":
        return AlertTriangle
      default:
        return Clock
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-destructive text-destructive-foreground"
      case "medium":
        return "bg-yellow-500 text-yellow-50"
      case "low":
        return "bg-green-500 text-green-50"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const HealthIcon = getHealthIcon(agent.healthStatus)

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-card border-border">
        <CardHeader className="border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <agent.icon className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">{agent.name}</CardTitle>
                <CardDescription>{agent.role}</CardDescription>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Status and Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <HealthIcon className="h-5 w-5" />
                <Badge className={getHealthColor(agent.healthStatus)}>{agent.healthStatus}</Badge>
              </div>
              <div className="text-sm text-muted-foreground">Model: {agent.modelVersion}</div>
              <div className="text-sm text-muted-foreground">
                Updated: {new Date(agent.lastUpdated).toLocaleString()}
              </div>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="mr-2 h-4 w-4" />
                Restart
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="mr-2 h-4 w-4" />
                Configure
              </Button>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-muted/30 border-border">
              <CardHeader>
                <CardTitle className="text-lg">Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Accuracy</span>
                    <span className="font-medium">{(agent.metrics.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${agent.metrics.accuracy * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Precision</span>
                    <span className="font-medium">{(agent.metrics.precision * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-chart-2 h-2 rounded-full"
                      style={{ width: `${agent.metrics.precision * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Recall</span>
                    <span className="font-medium">{(agent.metrics.recall * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-chart-3 h-2 rounded-full"
                      style={{ width: `${agent.metrics.recall * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">F1 Score</span>
                    <span className="font-medium">{(agent.metrics.f1Score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="bg-chart-4 h-2 rounded-full"
                      style={{ width: `${agent.metrics.f1Score * 100}%` }}
                    ></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-muted/30 border-border">
              <CardHeader>
                <CardTitle className="text-lg">Activity Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Flags This Week</span>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="font-medium text-foreground">{agent.flagsThisWeek}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Last Updated</span>
                  <span className="font-medium text-foreground">
                    {new Date(agent.lastUpdated).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge className={getHealthColor(agent.healthStatus)}>{agent.healthStatus}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-muted/30 border-border">
            <CardHeader>
              <CardTitle className="text-lg">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {agent.recentActivity.map((activity: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-background rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge className={getSeverityColor(activity.severity)}>{activity.severity}</Badge>
                      <span className="text-sm text-foreground">{activity.event}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{activity.time}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Configuration */}
          <Card className="bg-muted/30 border-border">
            <CardHeader>
              <CardTitle className="text-lg">Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(agent.configuration).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center p-2">
                    <span className="text-sm text-muted-foreground capitalize">
                      {key.replace(/([A-Z])/g, " $1").trim()}:
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {Array.isArray(value) ? value.join(", ") : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  )
}
