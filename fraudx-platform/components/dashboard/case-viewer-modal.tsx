"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  X,
  FileText,
  Image,
  Mic,
  Activity,
  User,
  CreditCard,
  MapPin,
  Clock,
  AlertTriangle,
  Play,
  Pause,
  Download,
} from "lucide-react"

interface CaseViewerModalProps {
  alert: any
  onClose: () => void
}

export function CaseViewerModal({ alert, onClose }: CaseViewerModalProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Open":
        return "bg-blue-500 text-blue-50"
      case "Escalated":
        return "bg-yellow-500 text-yellow-50"
      case "Resolved":
        return "bg-green-500 text-green-50"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-destructive text-destructive-foreground"
      case "Medium":
        return "bg-yellow-500 text-yellow-50"
      case "Low":
        return "bg-green-500 text-green-50"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-6xl max-h-[90vh] overflow-y-auto bg-card border-border">
        <CardHeader className="border-b border-border">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Case Viewer - {alert.id}</CardTitle>
              <CardDescription>{alert.description}</CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          {/* Case Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Card className="bg-muted/30 border-border">
              <CardHeader>
                <CardTitle className="text-lg">Case Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">User:</span>
                  <span className="text-sm font-medium text-foreground">{alert.affectedUser}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Card:</span>
                  <span className="text-sm font-medium text-foreground">****{alert.cardLast4}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Amount:</span>
                  <span className="text-sm font-medium text-foreground">{alert.amount}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Location:</span>
                  <span className="text-sm font-medium text-foreground">{alert.location}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Detected:</span>
                  <span className="text-sm font-medium text-foreground">{new Date(alert.date).toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-muted/30 border-border">
              <CardHeader>
                <CardTitle className="text-lg">Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Badge className={getStatusColor(alert.status)}>{alert.status}</Badge>
                  <Badge className={getPriorityColor(alert.priority)}>{alert.priority} Priority</Badge>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-muted-foreground">Risk Score</span>
                    <span className="font-medium text-destructive">{(alert.riskScore * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-3">
                    <div
                      className="bg-destructive h-3 rounded-full"
                      style={{ width: `${alert.riskScore * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Trigger Source:</span>
                  <p className="text-sm font-medium text-foreground mt-1">{alert.triggerSource}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Evidence Tabs */}
          <Tabs defaultValue="documents" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="documents" className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Documents</span>
              </TabsTrigger>
              <TabsTrigger value="images" className="flex items-center space-x-2">
                <Image className="h-4 w-4" />
                <span>Images</span>
              </TabsTrigger>
              <TabsTrigger value="audio" className="flex items-center space-x-2">
                <Mic className="h-4 w-4" />
                <span>Audio</span>
              </TabsTrigger>
              <TabsTrigger value="timeline" className="flex items-center space-x-2">
                <Activity className="h-4 w-4" />
                <span>Timeline</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="documents" className="mt-6">
              <Card className="bg-muted/30 border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Document Analysis</CardTitle>
                  <CardDescription>OCR results and tampering detection</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {alert.evidence.documents.map((doc: string, index: number) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-background rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-primary" />
                          <span className="font-medium">{doc}</span>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Download className="mr-2 h-4 w-4" />
                            Download
                          </Button>
                        </div>
                      </div>
                    ))}
                    {alert.evidence.metadata.ocrConfidence && (
                      <div className="mt-4 p-4 bg-destructive/10 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <AlertTriangle className="h-4 w-4 text-destructive" />
                          <span className="font-medium text-destructive">Low OCR Confidence</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          OCR confidence: {(alert.evidence.metadata.ocrConfidence * 100).toFixed(0)}%
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="images" className="mt-6">
              <Card className="bg-muted/30 border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Image Analysis</CardTitle>
                  <CardDescription>Visual evidence and tampering heatmaps</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {alert.evidence.images.map((image: string, index: number) => (
                      <div key={index} className="space-y-2">
                        <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                          <div className="text-center">
                            <Image className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground">{image}</p>
                          </div>
                        </div>
                        <Button variant="outline" size="sm" className="w-full bg-transparent">
                          <Download className="mr-2 h-4 w-4" />
                          Download {image}
                        </Button>
                      </div>
                    ))}
                  </div>
                  {alert.evidence.metadata.ganConfidence && (
                    <div className="mt-4 p-4 bg-destructive/10 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <AlertTriangle className="h-4 w-4 text-destructive" />
                        <span className="font-medium text-destructive">Deepfake Detected</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        GAN confidence: {(alert.evidence.metadata.ganConfidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="audio" className="mt-6">
              <Card className="bg-muted/30 border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Audio Analysis</CardTitle>
                  <CardDescription>Voice recordings and synthetic speech detection</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {alert.evidence.audio.length > 0 ? (
                      alert.evidence.audio.map((audio: string, index: number) => (
                        <div key={index} className="flex items-center justify-between p-4 bg-background rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Mic className="h-5 w-5 text-primary" />
                            <div>
                              <span className="font-medium">{audio}</span>
                              {alert.evidence.metadata.callDuration && (
                                <p className="text-sm text-muted-foreground">
                                  Duration: {alert.evidence.metadata.callDuration}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={() => setIsPlaying(!isPlaying)}>
                              {isPlaying ? <Pause className="mr-2 h-4 w-4" /> : <Play className="mr-2 h-4 w-4" />}
                              {isPlaying ? "Pause" : "Play"}
                            </Button>
                            <Button variant="outline" size="sm">
                              <Download className="mr-2 h-4 w-4" />
                              Download
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <Mic className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>No audio evidence available</p>
                      </div>
                    )}
                    {alert.evidence.metadata.voiceConfidence && (
                      <div className="mt-4 p-4 bg-destructive/10 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <AlertTriangle className="h-4 w-4 text-destructive" />
                          <span className="font-medium text-destructive">Synthetic Voice Detected</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Voice confidence: {(alert.evidence.metadata.voiceConfidence * 100).toFixed(0)}%
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="timeline" className="mt-6">
              <Card className="bg-muted/30 border-border">
                <CardHeader>
                  <CardTitle className="text-lg">Activity Timeline</CardTitle>
                  <CardDescription>Chronological sequence of user activity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-3 bg-background rounded-lg">
                      <div className="w-2 h-2 bg-destructive rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Fraud Alert Triggered</p>
                        <p className="text-xs text-muted-foreground">{new Date(alert.date).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-3 bg-background rounded-lg">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Transaction Attempted</p>
                        <p className="text-xs text-muted-foreground">
                          {alert.amount} at {alert.location}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-3 bg-background rounded-lg">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">User Authentication</p>
                        <p className="text-xs text-muted-foreground">Card verification initiated</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-border mt-6">
            <Button variant="outline">Export Case</Button>
            <Button variant="outline">Escalate</Button>
            <Button>Mark Resolved</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
