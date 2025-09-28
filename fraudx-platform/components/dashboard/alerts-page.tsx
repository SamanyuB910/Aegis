"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { CaseViewerModal } from "@/components/dashboard/case-viewer-modal"
import { Search, Filter, Download, Eye, Calendar } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const alerts = [
  {
    id: "ALT-2024-001",
    triggerSource: "Log Agent",
    affectedUser: "john.doe@email.com",
    cardLast4: "4532",
    amount: "$2,500",
    location: "New York, NY",
    date: "2024-01-15 14:32:00",
    status: "Open",
    priority: "High",
    description: "Multiple high-value transactions from different locations",
    riskScore: 0.89,
    evidence: {
      documents: ["Transaction Log", "Location Data"],
      images: ["Card Photo", "ID Verification"],
      audio: ["Verification Call"],
      metadata: {
        ipAddress: "192.168.1.100",
        deviceId: "DEV-12345",
        userAgent: "Mozilla/5.0...",
      },
    },
  },
  {
    id: "ALT-2024-002",
    triggerSource: "Document Agent",
    affectedUser: "jane.smith@email.com",
    cardLast4: "7891",
    amount: "$1,200",
    location: "Los Angeles, CA",
    date: "2024-01-15 13:45:00",
    status: "Escalated",
    priority: "High",
    description: "ID verification failed with tampering indicators",
    riskScore: 0.94,
    evidence: {
      documents: ["Driver License", "Utility Bill", "OCR Analysis"],
      images: ["Document Scan", "Tampering Heatmap"],
      audio: [],
      metadata: {
        ocrConfidence: 0.23,
        tamperingScore: 0.87,
      },
    },
  },
  {
    id: "ALT-2024-003",
    triggerSource: "Vision Agent",
    affectedUser: "fake.user@email.com",
    cardLast4: "1234",
    amount: "$350",
    location: "Chicago, IL",
    date: "2024-01-15 12:18:00",
    status: "Resolved",
    priority: "Medium",
    description: "AI-generated profile image detected",
    riskScore: 0.97,
    evidence: {
      documents: ["Profile Analysis"],
      images: ["Profile Image", "Deepfake Analysis"],
      audio: [],
      metadata: {
        ganConfidence: 0.97,
        pixelAnomalies: 23,
      },
    },
  },
  {
    id: "ALT-2024-004",
    triggerSource: "Voice Agent",
    affectedUser: "victim@email.com",
    cardLast4: "9876",
    amount: "$5,000",
    location: "Miami, FL",
    date: "2024-01-15 11:22:00",
    status: "Open",
    priority: "High",
    description: "Synthetic speech detected in verification call",
    riskScore: 0.91,
    evidence: {
      documents: ["Call Transcript"],
      images: [],
      audio: ["Verification Call", "Voice Analysis"],
      metadata: {
        callDuration: "2:34",
        voiceConfidence: 0.91,
        syntheticIndicators: 5,
      },
    },
  },
  {
    id: "ALT-2024-005",
    triggerSource: "Log Agent",
    affectedUser: "test.user@email.com",
    cardLast4: "5555",
    amount: "$750",
    location: "Seattle, WA",
    date: "2024-01-15 10:15:00",
    status: "Open",
    priority: "Medium",
    description: "Unusual spending pattern detected",
    riskScore: 0.76,
    evidence: {
      documents: ["Transaction History", "Spending Analysis"],
      images: [],
      audio: [],
      metadata: {
        patternDeviation: 0.82,
        historicalAverage: "$125",
      },
    },
  },
]

export function AlertsPage() {
  const [selectedAlert, setSelectedAlert] = useState<(typeof alerts)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

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

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      searchQuery === "" ||
      alert.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.affectedUser.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = statusFilter === "all" || alert.status.toLowerCase() === statusFilter.toLowerCase()

    return matchesSearch && matchesStatus
  })

  const alertStats = {
    total: alerts.length,
    open: alerts.filter((a) => a.status === "Open").length,
    escalated: alerts.filter((a) => a.status === "Escalated").length,
    resolved: alerts.filter((a) => a.status === "Resolved").length,
  }

  return (
    <>
      <div className="space-y-6">
        <div className="flex flex-col gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Alerts</h1>
            <p className="text-muted-foreground">Active fraud cases requiring attention</p>
          </div>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-2 sm:self-end">
            <Button variant="outline" size="sm" className="w-full sm:w-auto bg-transparent">
              <Calendar className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Last 30 days</span>
              <span className="sm:hidden">30 days</span>
            </Button>
            <Button variant="outline" size="sm" className="w-full sm:w-auto bg-transparent">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <Card className="bg-card border-border">
            <CardContent className="p-3 sm:p-4">
              <div className="text-xl sm:text-2xl font-bold text-foreground">{alertStats.total}</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Total Alerts</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-3 sm:p-4">
              <div className="text-xl sm:text-2xl font-bold text-blue-500">{alertStats.open}</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Open</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-3 sm:p-4">
              <div className="text-xl sm:text-2xl font-bold text-yellow-500">{alertStats.escalated}</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Escalated</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-3 sm:p-4">
              <div className="text-xl sm:text-2xl font-bold text-green-500">{alertStats.resolved}</div>
              <div className="text-xs sm:text-sm text-muted-foreground">Resolved</div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-card border-border">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search alerts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-48">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="escalated">Escalated</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Active Cases</CardTitle>
            <CardDescription>Fraud alerts requiring investigation or action</CardDescription>
          </CardHeader>
          <CardContent className="p-0 sm:p-6">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[120px]">Alert ID</TableHead>
                    <TableHead className="min-w-[120px]">Source</TableHead>
                    <TableHead className="min-w-[180px]">User</TableHead>
                    <TableHead className="min-w-[100px]">Amount</TableHead>
                    <TableHead className="min-w-[100px] hidden sm:table-cell">Date</TableHead>
                    <TableHead className="min-w-[80px]">Status</TableHead>
                    <TableHead className="min-w-[80px] hidden md:table-cell">Priority</TableHead>
                    <TableHead className="min-w-[120px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAlerts.map((alert) => (
                    <TableRow key={alert.id} className="hover:bg-muted/50">
                      <TableCell className="font-mono text-xs sm:text-sm">{alert.id}</TableCell>
                      <TableCell className="text-xs sm:text-sm">{alert.triggerSource}</TableCell>
                      <TableCell className="max-w-[120px] sm:max-w-[180px] truncate text-xs sm:text-sm">
                        {alert.affectedUser}
                      </TableCell>
                      <TableCell className="font-medium text-xs sm:text-sm">{alert.amount}</TableCell>
                      <TableCell className="text-xs text-muted-foreground hidden sm:table-cell">
                        {new Date(alert.date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge className={`${getStatusColor(alert.status)} text-xs`}>{alert.status}</Badge>
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        <Badge className={`${getPriorityColor(alert.priority)} text-xs`}>{alert.priority}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedAlert(alert)}
                          className="text-xs sm:text-sm"
                        >
                          <Eye className="mr-1 sm:mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                          <span className="hidden sm:inline">Open Case</span>
                          <span className="sm:hidden">Open</span>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Case Viewer Modal */}
      {selectedAlert && <CaseViewerModal alert={selectedAlert} onClose={() => setSelectedAlert(null)} />}
    </>
  )
}
