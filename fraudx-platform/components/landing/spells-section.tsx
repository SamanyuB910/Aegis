import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, Shield } from "lucide-react"

const spells = [
  {
    icon: AlertTriangle,
    title: "Escalate to Manual Review",
    description: "Automatically flags high-risk cases for human analyst review with complete context and evidence",
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
  },
  {
    icon: Shield,
    title: "Auto-Block Card",
    description: "Instantly blocks suspicious payment methods and notifies cardholders through secure channels",
    color: "text-destructive",
    bgColor: "bg-destructive/10",
  },
]

export function SpellsSection() {
  return (
    <section className="py-24 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Automation Spells</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Configurable automated responses that execute based on AI agent findings and risk thresholds
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {spells.map((spell, index) => (
            <Card key={index} className="bg-card border-border hover:border-primary/50 transition-colors group">
              <CardHeader>
                <div
                  className={`w-12 h-12 ${spell.bgColor} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <spell.icon className={`h-6 w-6 ${spell.color}`} />
                </div>
                <CardTitle className="text-xl">{spell.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-muted-foreground">{spell.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
