"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { InvestigationDetails } from "@/components/dashboard/investigation-details"
import { AlertTriangle, FileText, Eye, Mic, BarChart3, Clock, User, CreditCard, ChevronRight } from "lucide-react"

const investigations = [
  {
    id: "INV-2024-001",
    title: "Suspicious Card Activity Cluster",
    description: "Multiple high-value transactions from different locations",
    timestamp: "2024-01-15 14:32:00",
    status: "active",
    priority: "high",
    agent: "Log Agent",
    agentIcon: BarChart3,
    user: "john.doe@email.com",
    cardLast4: "4532",
    amount: "$2,500",
    location: "New York, NY",
    confidence: 0.89,
    flaggedReason: "Anomalous Location Pattern",
    details: {
      transactions: [
        { time: "14:30", amount: "$500", location: "NYC Store A", status: "flagged" },
        { time: "14:31", amount: "$750", location: "NYC Store B", status: "flagged" },
        { time: "14:32", amount: "$1,250", location: "NYC Store C", status: "blocked" },
      ],
      riskFactors: ["Rapid succession", "Geographic clustering", "Amount escalation"],
    },
  },
  {
    id: "INV-2024-002",
    title: "Document Forgery Detection",
    description: "ID verification failed with tampering indicators",
    timestamp: "2024-01-15 13:45:00",
    status: "escalated",
    priority: "high",
    agent: "Document Agent",
    agentIcon: FileText,
    user: "jane.smith@email.com",
    cardLast4: "7891",
    amount: "$1,200",
    location: "Los Angeles, CA",
    confidence: 0.94,
    flaggedReason: "Document Tampering Detected",
    details: {
      documents: ["Driver License", "Utility Bill"],
      tampering: ["Font inconsistency", "Digital artifacts", "Metadata anomalies"],
      ocrConfidence: 0.23,
    },
  },
  {
    id: "INV-2024-003",
    title: "Deepfake Profile Image",
    description: "AI-generated profile image detected",
    timestamp: "2024-01-15 12:18:00",
    status: "resolved",
    priority: "medium",
    agent: "Vision Agent",
    agentIcon: Eye,
    user: "fake.user@email.com",
    cardLast4: "1234",
    amount: "$350",
    location: "Chicago, IL",
    confidence: 0.97,
    flaggedReason: "Synthetic Image Detection",
    details: {
      imageAnalysis: "GAN-generated face detected",
      artifacts: ["Pixel inconsistencies", "Unnatural lighting", "Missing micro-expressions"],
      resolution: "Account suspended, user notified",
    },
  },
  {
    id: "INV-2024-004",
    title: "Voice Cloning Attempt",
    description: "Synthetic speech detected in verification call",
    timestamp: "2024-01-15 11:22:00",
    status: "active",
    priority: "high",
    agent: "Voice Agent",
    agentIcon: Mic,
    user: "victim@email.com",
    cardLast4: "9876",
    amount: "$5,000",
    location: "Miami, FL",
    confidence: 0.91,
    flaggedReason: "Synthetic Speech Patterns",
    details: {
      audioAnalysis: "Voice cloning technology detected",
      indicators: ["Unnatural prosody", "Spectral anomalies", "Missing vocal fry"],
      callDuration: "2:34",
    },
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "active":
      return "bg-blue-500 text-blue-50"
    case "escalated":
      return "bg-yellow-500 text-yellow-50"
    case "resolved":
      return "bg-green-500 text-green-50"
    default:
      return "bg-muted text-muted-foreground"
  }
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
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

export function InvestigationTimeline() {
  const [selectedInvestigation, setSelectedInvestigation] = useState<(typeof investigations)[0] | null>(null)

  return (
    <>
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Investigation Timeline</CardTitle>
          <CardDescription>Chronological view of suspicious activity clusters</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {investigations.map((investigation, index) => (
              <div key={investigation.id} className="relative">
                {/* Timeline line */}
                {index < investigations.length - 1 && (
                  <div className="absolute left-6 top-12 w-0.5 h-16 bg-border"></div>
                )}

                {/* Investigation node */}
                <div
                  className="flex items-start space-x-4 p-4 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedInvestigation(investigation)}
                >
                  {/* Agent icon */}
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <investigation.agentIcon className="h-6 w-6 text-primary" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-foreground">{investigation.title}</h3>
                        <Badge className={getStatusColor(investigation.status)}>{investigation.status}</Badge>
                        <Badge className={getPriorityColor(investigation.priority)}>{investigation.priority}</Badge>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{investigation.description}</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{investigation.user}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CreditCard className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">*{investigation.cardLast4}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{investigation.amount}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">
                          {new Date(investigation.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">Flagged by:</span>
                        <span className="text-sm font-medium text-foreground">{investigation.agent}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">Confidence:</span>
                        <span className="text-sm font-medium text-foreground">
                          {(investigation.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Investigation Details Modal */}
      {selectedInvestigation && (
        <InvestigationDetails investigation={selectedInvestigation} onClose={() => setSelectedInvestigation(null)} />
      )}
    </>
  )
}
