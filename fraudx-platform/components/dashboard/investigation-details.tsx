"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  X,
  AlertTriangle,
  Clock,
  User,
  CreditCard,
  MapPin,
  TrendingUp,
  FileText,
  Eye,
  Mic,
  BarChart3,
} from "lucide-react"

interface InvestigationDetailsProps {
  investigation: any
  onClose: () => void
}

export function InvestigationDetails({ investigation, onClose }: InvestigationDetailsProps) {
  const getAgentIcon = (agent: string) => {
    switch (agent) {
      case "Log Agent":
        return BarChart3
      case "Document Agent":
        return FileText
      case "Vision Agent":
        return Eye
      case "Voice Agent":
        return Mic
      default:
        return AlertTriangle
    }
  }

  const AgentIcon = getAgentIcon(investigation.agent)

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-card border-border">
        <CardHeader className="border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <AgentIcon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">{investigation.title}</CardTitle>
                <CardDescription>Case ID: {investigation.id}</CardDescription>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Status and Priority */}
          <div className="flex items-center space-x-4">
            <Badge
              className={
                investigation.status === "active"
                  ? "bg-blue-500 text-blue-50"
                  : investigation.status === "escalated"
                    ? "bg-yellow-500 text-yellow-50"
                    : "bg-green-500 text-green-50"
              }
            >
              {investigation.status}
            </Badge>
            <Badge
              className={
                investigation.priority === "high"
                  ? "bg-destructive text-destructive-foreground"
                  : investigation.priority === "medium"
                    ? "bg-yellow-500 text-yellow-50"
                    : "bg-green-500 text-green-50"
              }
            >
              {investigation.priority} priority
            </Badge>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Confidence: {(investigation.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Case Information</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">User:</span>
                  <span className="text-sm font-medium text-foreground">{investigation.user}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Card:</span>
                  <span className="text-sm font-medium text-foreground">****{investigation.cardLast4}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Amount:</span>
                  <span className="text-sm font-medium text-foreground">{investigation.amount}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Location:</span>
                  <span className="text-sm font-medium text-foreground">{investigation.location}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Detected:</span>
                  <span className="text-sm font-medium text-foreground">
                    {new Date(investigation.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Detection Details</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-muted-foreground">Flagged Reason:</span>
                  <p className="text-sm font-medium text-foreground mt-1">{investigation.flaggedReason}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Responsible Agent:</span>
                  <p className="text-sm font-medium text-foreground mt-1">{investigation.agent}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Description:</span>
                  <p className="text-sm text-muted-foreground mt-1">{investigation.description}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Agent-specific Details */}
          {investigation.details && (
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Analysis Details</h3>
              <Card className="bg-muted/30 border-border">
                <CardContent className="p-4">
                  {investigation.agent === "Log Agent" && investigation.details.transactions && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-foreground">Transaction Timeline</h4>
                      {investigation.details.transactions.map((tx: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-background rounded">
                          <div className="flex items-center space-x-3">
                            <span className="text-sm font-mono">{tx.time}</span>
                            <span className="text-sm">{tx.amount}</span>
                            <span className="text-sm text-muted-foreground">{tx.location}</span>
                          </div>
                          <Badge
                            className={
                              tx.status === "blocked"
                                ? "bg-destructive text-destructive-foreground"
                                : "bg-yellow-500 text-yellow-50"
                            }
                          >
                            {tx.status}
                          </Badge>
                        </div>
                      ))}
                      <div className="mt-3">
                        <span className="text-sm text-muted-foreground">Risk Factors:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {investigation.details.riskFactors.map((factor: string, index: number) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {factor}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {investigation.agent === "Document Agent" && investigation.details.documents && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-foreground">Document Analysis</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-muted-foreground">Documents Analyzed:</span>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {investigation.details.documents.map((doc: string, index: number) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {doc}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <span className="text-sm text-muted-foreground">Tampering Indicators:</span>
                          <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                            {investigation.details.tampering.map((indicator: string, index: number) => (
                              <li key={index}>{indicator}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <span className="text-sm text-muted-foreground">OCR Confidence:</span>
                          <span className="text-sm font-medium text-destructive ml-2">
                            {(investigation.details.ocrConfidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {investigation.agent === "Vision Agent" && investigation.details.imageAnalysis && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-foreground">Image Analysis</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-muted-foreground">Analysis Result:</span>
                          <p className="text-sm font-medium text-foreground mt-1">
                            {investigation.details.imageAnalysis}
                          </p>
                        </div>
                        <div>
                          <span className="text-sm text-muted-foreground">Detected Artifacts:</span>
                          <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                            {investigation.details.artifacts.map((artifact: string, index: number) => (
                              <li key={index}>{artifact}</li>
                            ))}
                          </ul>
                        </div>
                        {investigation.details.resolution && (
                          <div>
                            <span className="text-sm text-muted-foreground">Resolution:</span>
                            <p className="text-sm font-medium text-green-600 mt-1">
                              {investigation.details.resolution}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {investigation.agent === "Voice Agent" && investigation.details.audioAnalysis && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-foreground">Voice Analysis</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-muted-foreground">Analysis Result:</span>
                          <p className="text-sm font-medium text-foreground mt-1">
                            {investigation.details.audioAnalysis}
                          </p>
                        </div>
                        <div>
                          <span className="text-sm text-muted-foreground">Synthetic Indicators:</span>
                          <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                            {investigation.details.indicators.map((indicator: string, index: number) => (
                              <li key={index}>{indicator}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <span className="text-sm text-muted-foreground">Call Duration:</span>
                          <span className="text-sm font-medium text-foreground ml-2">
                            {investigation.details.callDuration}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-border">
            <Button variant="outline">Export Report</Button>
            <Button variant="outline">Escalate Case</Button>
            <Button>Mark Resolved</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
