"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

const data = [
  { name: "Mon", transactions: 85, documents: 23, images: 12, voice: 8 },
  { name: "Tue", transactions: 92, documents: 31, images: 18, voice: 15 },
  { name: "Wed", transactions: 78, documents: 28, images: 22, voice: 11 },
  { name: "Thu", transactions: 96, documents: 35, images: 16, voice: 19 },
  { name: "Fri", transactions: 89, documents: 29, images: 25, voice: 13 },
  { name: "Sat", transactions: 67, documents: 18, images: 14, voice: 7 },
  { name: "Sun", transactions: 54, documents: 12, images: 9, voice: 5 },
]

export function WeeklyGraph() {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Anomaly Detection Trends</CardTitle>
            <CardDescription>Weekly anomaly scores by agent type</CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              Week
            </Button>
            <Button variant="ghost" size="sm">
              Month
            </Button>
            <Button variant="ghost" size="sm">
              Year
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="name" className="text-muted-foreground" fontSize={12} />
              <YAxis className="text-muted-foreground" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="transactions"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                name="Transactions"
              />
              <Line type="monotone" dataKey="documents" stroke="hsl(var(--chart-2))" strokeWidth={2} name="Documents" />
              <Line type="monotone" dataKey="images" stroke="hsl(var(--chart-3))" strokeWidth={2} name="Images" />
              <Line type="monotone" dataKey="voice" stroke="hsl(var(--chart-4))" strokeWidth={2} name="Voice" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
