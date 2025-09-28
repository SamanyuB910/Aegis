"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ChevronRight, AlertTriangle, CheckCircle, Clock } from "lucide-react"

interface AgentCardProps {
  agent: any
  onClick: () => void
}

export function AgentCard({ agent, onClick }: AgentCardProps) {
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

  const HealthIcon = getHealthIcon(agent.healthStatus)

  return (
    <Card
      className="bg-card border-border hover:border-primary/50 transition-colors cursor-pointer group"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <agent.icon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{agent.name}</CardTitle>
              <CardDescription>{agent.role}</CardDescription>
            </div>
          </div>
          <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{agent.description}</p>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Model Version:</span>
            <div className="font-medium text-foreground">{agent.modelVersion}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Flags This Week:</span>
            <div className="font-medium text-foreground">{agent.flagsThisWeek}</div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <HealthIcon className="h-4 w-4" />
            <Badge className={getHealthColor(agent.healthStatus)}>{agent.healthStatus}</Badge>
          </div>
          <div className="text-xs text-muted-foreground">
            Updated {new Date(agent.lastUpdated).toLocaleDateString()}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Accuracy</span>
            <span className="font-medium">{(agent.metrics.accuracy * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${agent.metrics.accuracy * 100}%` }}
            ></div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
