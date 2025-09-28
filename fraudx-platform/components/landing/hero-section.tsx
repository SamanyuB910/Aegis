import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"
import Link from "next/link"

export function HeroSection() {
  return (
    <section className="py-16 sm:py-24 px-4 text-center animate-fade-in">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-4 sm:mb-6">
          <span className="text-primary text-sm font-medium tracking-wide uppercase">FraudX for Enterprise</span>
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold mb-4 sm:mb-6 text-balance">
          Redefining <span className="gradient-text">Fraud Detection</span>
        </h1>
        <p className="text-lg sm:text-xl text-muted-foreground mb-8 sm:mb-12 max-w-2xl mx-auto text-pretty">
          Multi-agent AI system for transactions, documents, images, and voice fraud detection. Empower your security
          team with intelligent automation and explainable AI insights.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center max-w-md sm:max-w-none mx-auto">
          <Button size="lg" className="glow-primary w-full sm:w-auto" asChild>
            <Link href="/dashboard">
              Launch Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" className="group bg-transparent w-full sm:w-auto" asChild>
            <Link href="#demo">
              <Play className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
              Watch Demo
            </Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
