import { Card, CardContent } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"

const steps = [
  {
    step: "01",
    title: "Data Ingestion",
    description: "Real-time streaming of transactions, documents, images, and voice data through secure APIs",
  },
  {
    step: "02",
    title: "Multi-Agent Analysis",
    description: "Four specialized AI agents analyze different data types simultaneously for comprehensive coverage",
  },
  {
    step: "03",
    title: "Risk Scoring",
    description: "Advanced ML models generate explainable risk scores with confidence intervals and reasoning",
  },
  {
    step: "04",
    title: "Automated Response",
    description: "Configurable spells trigger automated actions based on risk thresholds and business rules",
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 px-4 bg-muted/30">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">How FraudX Works</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Intelligent fraud detection pipeline powered by multi-agent AI architecture
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <Card className="bg-card border-border h-full">
                <CardContent className="p-6">
                  <div className="text-primary text-sm font-mono font-bold mb-2">{step.step}</div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground text-sm">{step.description}</p>
                </CardContent>
              </Card>
              {index < steps.length - 1 && (
                <ArrowRight className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 text-primary h-6 w-6" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
