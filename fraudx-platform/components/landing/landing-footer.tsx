import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Github, Mail } from "lucide-react"
import Link from "next/link"

export function LandingFooter() {
  return (
    <footer className="border-t border-border bg-background py-16 px-4">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="col-span-1 md:col-span-2">
            <div className="text-2xl font-mono font-bold mb-4">FRAUDX</div>
            <p className="text-muted-foreground mb-6 max-w-md">
              Next-generation fraud detection platform powered by multi-agent AI. Secure your business with intelligent
              automation.
            </p>
            <div className="flex space-x-4">
              <Button variant="outline" size="icon" asChild>
                <Link href="https://github.com" aria-label="GitHub">
                  <Github className="h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="icon" asChild>
                <Link href="mailto:contact@fraudx.ai" aria-label="Email">
                  <Mail className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#features" className="hover:text-foreground transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#how-it-works" className="hover:text-foreground transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-foreground transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Newsletter</h3>
            <p className="text-sm text-muted-foreground mb-4">Stay updated with the latest in fraud detection AI</p>
            <div className="flex space-x-2">
              <Input placeholder="Enter your email" className="flex-1" />
              <Button size="sm">Subscribe</Button>
            </div>
          </div>
        </div>
        <div className="border-t border-border pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
          <p>&copy; 2025 FraudX. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link href="/terms" className="hover:text-foreground transition-colors">
              Terms
            </Link>
            <Link href="/privacy" className="hover:text-foreground transition-colors">
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
