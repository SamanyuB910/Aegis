"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Menu, X } from "lucide-react"

export function LandingHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="text-2xl font-mono font-bold text-foreground">
            FRAUDX
          </Link>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
              How It Works
            </Link>
            <Link href="#technology" className="text-muted-foreground hover:text-foreground transition-colors">
              Technology
            </Link>
          </nav>
        </div>

        <div className="hidden md:flex items-center space-x-4">
          <Button variant="ghost" asChild>
            <Link href="/dashboard">Launch Dashboard</Link>
          </Button>
          <Button asChild>
            <Link href="#demo">Request Demo</Link>
          </Button>
        </div>

        <div className="md:hidden">
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="md:hidden border-t border-border bg-background/95 backdrop-blur-sm">
          <nav className="container mx-auto px-4 py-4 space-y-4">
            <Link
              href="#features"
              className="block text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Features
            </Link>
            <Link
              href="#how-it-works"
              className="block text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              How It Works
            </Link>
            <Link
              href="#technology"
              className="block text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Technology
            </Link>
            <div className="pt-4 space-y-2">
              <Button variant="ghost" asChild className="w-full justify-start">
                <Link href="/dashboard">Launch Dashboard</Link>
              </Button>
              <Button asChild className="w-full">
                <Link href="#demo">Request Demo</Link>
              </Button>
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}
