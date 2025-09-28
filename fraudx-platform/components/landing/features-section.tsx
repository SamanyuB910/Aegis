import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, Eye, Mic, BarChart3 } from "lucide-react"

const features = [
  {
    icon: BarChart3,
    title: "Log Agent",
    description: "Analyzes transaction patterns and behavioral anomalies in real-time with advanced ML models.",
  },
  {
    icon: FileText,
    title: "Document Agent",
    description: "OCR-powered document verification detecting forgeries, tampering, and inconsistencies.",
  },
  {
    icon: Eye,
    title: "Vision Agent",
    description: "Computer vision analysis for image authenticity, deepfake detection, and visual fraud patterns.",
  },
  {
    icon: Mic,
    title: "Voice Agent",
    description: "Voice biometrics and speech analysis to identify synthetic audio and voice cloning attempts.",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-16 sm:py-24 px-4 animate-slide-up">
      <div className="container mx-auto">
        <div className="text-center mb-12 sm:mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">FraudX Copilot Agents</h2>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            Four specialized AI agents working together to provide comprehensive fraud detection coverage
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="bg-card border-border hover:border-primary/50 transition-colors group">
              <CardHeader className="pb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-lg sm:text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <CardDescription className="text-muted-foreground text-sm sm:text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
