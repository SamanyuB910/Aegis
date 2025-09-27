import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { FileImage, Mic, Network, Upload, CheckCircle, AlertCircle } from "lucide-react"

const analysisResults = [
  {
    type: "Receipt Verification",
    icon: FileImage,
    status: "completed",
    confidence: 92,
    result: "Authentic",
    details: "OCR analysis confirms receipt authenticity",
  },
  {
    type: "Voice Analysis",
    icon: Mic,
    status: "processing",
    confidence: 78,
    result: "Stress Detected",
    details: "Elevated stress indicators in voice pattern",
  },
  {
    type: "Merchant Network",
    icon: Network,
    status: "completed",
    confidence: 85,
    result: "Suspicious Pattern",
    details: "3 connected merchants flagged in network",
  },
]

export function MultimodalAnalysis() {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="text-foreground">Multimodal AI Analysis</CardTitle>
        <p className="text-sm text-muted-foreground">Upload evidence for comprehensive fraud detection</p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <Button variant="outline" className="h-20 flex-col gap-2 bg-transparent">
            <FileImage className="h-5 w-5" />
            <span className="text-xs">Receipt</span>
          </Button>
          <Button variant="outline" className="h-20 flex-col gap-2 bg-transparent">
            <Mic className="h-5 w-5" />
            <span className="text-xs">Voice</span>
          </Button>
          <Button variant="outline" className="h-20 flex-col gap-2 bg-transparent">
            <Upload className="h-5 w-5" />
            <span className="text-xs">Upload</span>
          </Button>
        </div>

        <div className="space-y-4">
          {analysisResults.map((analysis, index) => (
            <div key={index} className="p-4 rounded-lg border bg-card/30">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <analysis.icon className="h-4 w-4 text-primary" />
                  <span className="font-medium text-foreground">{analysis.type}</span>
                </div>
                {analysis.status === "completed" ? (
                  <CheckCircle className="h-4 w-4 text-success" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-warning" />
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Confidence</span>
                  <span className="text-foreground">{analysis.confidence}%</span>
                </div>
                <Progress value={analysis.confidence} className="h-2" />

                <div className="flex items-center justify-between mt-3">
                  <Badge
                    variant={analysis.result === "Authentic" ? "default" : "destructive"}
                    className={
                      analysis.result === "Authentic"
                        ? "bg-success/10 text-success"
                        : "bg-destructive/10 text-destructive"
                    }
                  >
                    {analysis.result}
                  </Badge>
                </div>

                <p className="text-xs text-muted-foreground mt-2">{analysis.details}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
