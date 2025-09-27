import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building2, CreditCard, MapPin } from "lucide-react"

const transactions = [
  {
    id: "TXN-2024-001",
    bank: "Capital One Bank",
    merchant: "QuickMart #247",
    amount: "$127.45",
    location: "New York, NY",
    status: "flagged",
    time: "2:34 PM",
  },
  {
    id: "TXN-2024-002",
    bank: "Chase Bank",
    merchant: "TechStore Online",
    amount: "$899.99",
    location: "Online",
    status: "reviewing",
    time: "2:31 PM",
  },
  {
    id: "TXN-2024-003",
    bank: "Wells Fargo",
    merchant: "FuelStop #89",
    amount: "$67.23",
    location: "Los Angeles, CA",
    status: "cleared",
    time: "2:28 PM",
  },
  {
    id: "TXN-2024-004",
    bank: "Capital One Bank",
    merchant: "Restaurant Plaza",
    amount: "$45.67",
    location: "Chicago, IL",
    status: "cleared",
    time: "2:25 PM",
  },
  {
    id: "TXN-2024-005",
    bank: "Chase Bank",
    merchant: "Electronics Hub",
    amount: "$1,234.56",
    location: "Miami, FL",
    status: "flagged",
    time: "2:22 PM",
  },
]

const statusColors = {
  flagged: "bg-destructive/10 text-destructive",
  reviewing: "bg-warning/10 text-warning",
  cleared: "bg-success/10 text-success",
}

export function TransactionFeed() {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          <CreditCard className="h-5 w-5 text-primary" />
          Live Transaction Feed
        </CardTitle>
        <p className="text-sm text-muted-foreground">Recent transactions from connected banking APIs</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="flex items-center justify-between p-3 rounded-lg border bg-card/30">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Building2 className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <div className="font-medium text-foreground">{transaction.merchant}</div>
                  <div className="text-sm text-muted-foreground flex items-center gap-2">
                    <span>{transaction.bank}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {transaction.location}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-medium text-foreground">{transaction.amount}</div>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={statusColors[transaction.status as keyof typeof statusColors]} variant="secondary">
                    {transaction.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{transaction.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
