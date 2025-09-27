import { BarChart3, FileText, Home, Mic, Network, Receipt, Search, Settings, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Dashboard", icon: Home, current: true },
  { name: "Cases", icon: FileText, current: false },
  { name: "Analytics", icon: BarChart3, current: false },
  { name: "Transactions", icon: TrendingUp, current: false },
]

const analysis = [
  { name: "Receipt Verification", icon: Receipt },
  { name: "Voice Analysis", icon: Mic },
  { name: "Merchant Network", icon: Network },
  { name: "Pattern Detection", icon: Search },
]

export function DashboardSidebar() {
  return (
    <aside className="w-72 border-r border-border/30 bg-background/50 backdrop-blur-md">
      <div className="p-8">
        <nav className="space-y-10">
          <div>
            <h3 className="mb-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Main</h3>
            <div className="space-y-2">
              {navigation.map((item) => (
                <Button
                  key={item.name}
                  variant={item.current ? "default" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-4 h-12 text-base font-medium",
                    item.current
                      ? "bg-primary text-primary-foreground shadow-lg"
                      : "text-foreground hover:bg-card hover:text-card-foreground",
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="mb-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">AI Analysis</h3>
            <div className="space-y-2">
              {analysis.map((item) => (
                <Button
                  key={item.name}
                  variant="ghost"
                  className="w-full justify-start gap-4 h-12 text-base font-medium text-foreground hover:bg-card hover:text-card-foreground"
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Button>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-border/30">
            <Button
              variant="ghost"
              className="w-full justify-start gap-4 h-12 text-base font-medium text-foreground hover:bg-card hover:text-card-foreground"
            >
              <Settings className="h-5 w-5" />
              Settings
            </Button>
          </div>
        </nav>
      </div>
    </aside>
  )
}
