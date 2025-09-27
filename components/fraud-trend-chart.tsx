"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { time: "00:00", fraudCases: 12, transactions: 2400 },
  { time: "04:00", fraudCases: 8, transactions: 1800 },
  { time: "08:00", fraudCases: 24, transactions: 4200 },
  { time: "12:00", fraudCases: 18, transactions: 3800 },
  { time: "16:00", fraudCases: 32, transactions: 5200 },
  { time: "20:00", fraudCases: 28, transactions: 4800 },
  { time: "24:00", fraudCases: 15, transactions: 2800 },
]

export function FraudTrendChart() {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="text-foreground">Fraud Detection Trends</CardTitle>
        <p className="text-sm text-muted-foreground">Real-time fraud cases and transaction volume over 24 hours</p>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  color: "hsl(var(--foreground))",
                }}
              />
              <Line
                type="monotone"
                dataKey="fraudCases"
                stroke="hsl(var(--destructive))"
                strokeWidth={2}
                name="Fraud Cases"
              />
              <Line
                type="monotone"
                dataKey="transactions"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                name="Transactions (x100)"
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
