"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AgentCard } from "@/components/dashboard/agent-card"
import { AgentDetails } from "@/components/dashboard/agent-details"
import { BarChart3, FileText, Eye, Mic, RefreshCw, Settings, TrendingUp } from "lucide-react"

const agents = [
  {
    id: "log-agent",
    name: "Log Agent",
    role: "Transaction Analysis",
    icon: BarChart3,
    modelVersion: "v3.2.1",
    lastUpdated: "2024-01-15 09:30:00",
    flagsThisWeek: 47,
    healthStatus: "OK",
    description: "Analyzes transaction patterns and behavioral anomalies using advanced ML models",
    metrics: {
      accuracy: 0.94,
      precision: 0.91,
      recall: 0.89,
      f1Score: 0.9,
    },
    recentActivity: [
      { time: "14:32", event: "High-risk transaction flagged", severity: "high" },
      { time: "13:45", event: "Pattern analysis completed", severity: "low" },
      { time: "12:18", event: "Model inference successful", severity: "low" },
    ],
    configuration: {
      threshold: 0.75,
      batchSize: 1000,
      processingMode: "real-time",
    },
  },
  {
    id: "document-agent",
    name: "Document Agent",
    role: "Document Verification",
    icon: FileText,
    modelVersion: "v2.8.4",
    lastUpdated: "2024-01-14 16:45:00",
    flagsThisWeek: 23,
    healthStatus: "OK",
    description: "OCR-powered document verification detecting forgeries and tampering",
    metrics: {
      accuracy: 0.97,
      precision: 0.95,
      recall: 0.92,
      f1Score: 0.93,
    },
    recentActivity: [
      { time: "15:20", event: "Document tampering detected", severity: "high" },
      { time: "14:10", event: "OCR processing completed", severity: "low" },
      { time: "13:30", event: "Batch verification finished", severity: "low" },
    ],
    configuration: {
      ocrConfidence: 0.85,
      tamperingThreshold: 0.7,
      supportedFormats: ["PDF", "JPG", "PNG"],
    },
  },
  {
    id: "vision-agent",
    name: "Vision Agent",
    role: "Image Analysis",
    icon: Eye,
    modelVersion: "v4.1.0",
    lastUpdated: "2024-01-15 11:20:00",
    flagsThisWeek: 12,
    healthStatus: "Warning",
    description: "Computer vision analysis for image authenticity and deepfake detection",
    metrics: {
      accuracy: 0.96,
      precision: 0.94,
      recall: 0.88,
      f1Score: 0.91,
    },
    recentActivity: [
      { time: "16:15", event: "Deepfake detection successful", severity: "medium" },
      { time: "15:45", event: "Image processing queue full", severity: "medium" },
      { time: "14:30", event: "Model updated successfully", severity: "low" },
    ],
    configuration: {
      deepfakeThreshold: 0.8,
      imageResolution: "1024x1024",
      processingQueue: 500,
    },
  },
  {
    id: "voice-agent",
    name: "Voice Agent",
    role: "Voice Biometrics",
    icon: Mic,
    modelVersion: "v1.9.2",
    lastUpdated: "2024-01-13 14:15:00",
    flagsThisWeek: 8,
    healthStatus: "Offline",
    description: "Voice biometrics and speech analysis for synthetic audio detection",
    metrics: {
      accuracy: 0.92,
      precision: 0.89,
      recall: 0.85,
      f1Score: 0.87,
    },
    recentActivity: [
      { time: "12:00", event: "Agent went offline", severity: "high" },
      { time: "11:30", event: "Voice cloning detected", severity: "high" },
      { time: "10:45", event: "Audio processing completed", severity: "low" },
    ],
    configuration: {
      voiceprintThreshold: 0.78,
      audioQuality: "16kHz",
      maxCallDuration: "10min",
    },
  },
]

export function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<(typeof agents)[0] | null>(null)

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

  const healthStats = {
    total: agents.length,
    healthy: agents.filter((a) => a.healthStatus === "OK").length,
    warning: agents.filter((a) => a.healthStatus === "Warning").length,
    offline: agents.filter((a) => a.healthStatus === "Offline").length,
  }

  return (
    <>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">AI Agents</h1>
            <p className="text-muted-foreground">Monitor and manage fraud detection agents</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh Status
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              Global Settings
            </Button>
          </div>
        </div>

        {/* Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-foreground">{healthStats.total}</div>
                  <div className="text-sm text-muted-foreground">Total Agents</div>
                </div>
                <TrendingUp className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-green-500">{healthStats.healthy}</div>
                  <div className="text-sm text-muted-foreground">Healthy</div>
                </div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-yellow-500">{healthStats.warning}</div>
                  <div className="text-sm text-muted-foreground">Warning</div>
                </div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-destructive">{healthStats.offline}</div>
                  <div className="text-sm text-muted-foreground">Offline</div>
                </div>
                <div className="w-3 h-3 bg-destructive rounded-full"></div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Agents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} onClick={() => setSelectedAgent(agent)} />
          ))}
        </div>
      </div>

      {/* Agent Details Modal */}
      {selectedAgent && <AgentDetails agent={selectedAgent} onClose={() => setSelectedAgent(null)} />}
    </>
  )
}
