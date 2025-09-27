import { Bell, Search, Settings, Shield, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

export function DashboardHeader() {
  return (
    <header className="border-b border-border/30 bg-background/80 backdrop-blur-md">
      <div className="flex h-20 items-center justify-between px-8">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary/10 animate-glow">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">FraudX+</h1>
              <p className="text-sm text-muted-foreground font-medium">Copilot</p>
            </div>
          </div>
          <Badge className="bg-primary text-primary-foreground font-medium px-3 py-1">Production</Badge>
        </div>

        <div className="flex items-center gap-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search cases, merchants, transactions..."
              className="w-96 pl-12 h-12 bg-card border-0 shadow-sm text-card-foreground placeholder:text-card-foreground/50"
            />
          </div>

          <Button variant="ghost" size="icon" className="relative h-12 w-12 hover:bg-card">
            <Bell className="h-5 w-5 text-foreground" />
            <Badge className="absolute -right-1 -top-1 h-5 w-5 rounded-full bg-destructive p-0 text-xs animate-pulse-alert">
              3
            </Badge>
          </Button>

          <Button variant="ghost" size="icon" className="h-12 w-12 hover:bg-card">
            <Settings className="h-5 w-5 text-foreground" />
          </Button>

          <Button variant="ghost" size="icon" className="h-12 w-12 hover:bg-card">
            <User className="h-5 w-5 text-foreground" />
          </Button>
        </div>
      </div>
    </header>
  )
}
