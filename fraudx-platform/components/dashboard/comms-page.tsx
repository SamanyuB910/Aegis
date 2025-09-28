"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Phone, Video, MoreVertical, Search, Hash, Users, Bell, Menu, X } from "lucide-react"

interface Message {
  id: string
  user: string
  avatar: string
  content: string
  timestamp: string
  type: "message" | "system" | "alert"
}

interface Channel {
  id: string
  name: string
  type: "channel" | "dm"
  unread?: number
  online?: boolean
}

export function CommsPage() {
  const [selectedChannel, setSelectedChannel] = useState("general")
  const [message, setMessage] = useState("")
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const channels: Channel[] = [
    { id: "general", name: "general", type: "channel", unread: 3 },
    { id: "fraud-alerts", name: "fraud-alerts", type: "channel", unread: 12 },
    { id: "investigations", name: "investigations", type: "channel" },
    { id: "agent-updates", name: "agent-updates", type: "channel", unread: 1 },
    { id: "sarah", name: "Sarah Chen", type: "dm", online: true },
    { id: "mike", name: "Mike Rodriguez", type: "dm", online: true },
    { id: "alex", name: "Alex Thompson", type: "dm" },
  ]

  const messages: Message[] = [
    {
      id: "1",
      user: "Sarah Chen",
      avatar: "/professional-woman.png",
      content:
        "New suspicious pattern detected in the payment gateway. Agent Phoenix flagged 47 transactions in the last hour.",
      timestamp: "10:30 AM",
      type: "alert",
    },
    {
      id: "2",
      user: "Mike Rodriguez",
      avatar: "/man-analyst.jpg",
      content:
        "I'm investigating the cluster from yesterday. The ML confidence is at 94% - definitely looks like coordinated fraud.",
      timestamp: "10:32 AM",
      type: "message",
    },
    {
      id: "3",
      user: "System",
      avatar: "",
      content: "Case #FR-2024-0156 has been escalated to high priority",
      timestamp: "10:35 AM",
      type: "system",
    },
    {
      id: "4",
      user: "Alex Thompson",
      avatar: "/person-security.jpg",
      content:
        "Can someone review the velocity rules? We're getting too many false positives on legitimate high-value transactions.",
      timestamp: "10:38 AM",
      type: "message",
    },
    {
      id: "5",
      user: "Sarah Chen",
      avatar: "/professional-woman.png",
      content:
        "I'll take a look at the velocity thresholds. The new merchant onboarding might be affecting the baseline.",
      timestamp: "10:40 AM",
      type: "message",
    },
  ]

  const handleSendMessage = () => {
    if (message.trim()) {
      // Handle message sending logic here
      setMessage("")
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      <div className="md:hidden fixed top-20 left-4 z-50">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="bg-background/80 backdrop-blur-sm"
        >
          {isSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      <div
        className={`${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 fixed md:relative z-40 w-64 border-r border-border bg-card transition-transform duration-200 ease-in-out`}
      >
        <div className="p-4 border-b border-border bg-card">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">FX</span>
            </div>
            <span className="font-semibold">FraudX Team</span>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input placeholder="Search conversations..." className="pl-9" />
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2">
            <div className="mb-4">
              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Channels
              </div>
              {channels
                .filter((c) => c.type === "channel")
                .map((channel) => (
                  <button
                    key={channel.id}
                    onClick={() => setSelectedChannel(channel.id)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent ${
                      selectedChannel === channel.id ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                    }`}
                  >
                    <Hash className="w-4 h-4" />
                    <span className="flex-1 text-left">{channel.name}</span>
                    {channel.unread && (
                      <Badge variant="destructive" className="text-xs px-1.5 py-0.5 min-w-[1.25rem] h-5">
                        {channel.unread}
                      </Badge>
                    )}
                  </button>
                ))}
            </div>

            <div>
              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Direct Messages
              </div>
              {channels
                .filter((c) => c.type === "dm")
                .map((channel) => (
                  <button
                    key={channel.id}
                    onClick={() => setSelectedChannel(channel.id)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent ${
                      selectedChannel === channel.id ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                    }`}
                  >
                    <div className="relative">
                      <div className="w-2 h-2 rounded-full bg-muted-foreground" />
                      {channel.online && (
                        <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-green-500 border border-background" />
                      )}
                    </div>
                    <span className="flex-1 text-left">{channel.name}</span>
                  </button>
                ))}
            </div>
          </div>
        </ScrollArea>
      </div>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-border bg-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Hash className="w-5 h-5 text-muted-foreground" />
              <h2 className="font-semibold">{selectedChannel}</h2>
              <Badge variant="secondary" className="text-xs hidden sm:flex">
                <Users className="w-3 h-3 mr-1" />4 members
              </Badge>
            </div>
            <div className="flex items-center gap-1 sm:gap-2">
              <Button variant="ghost" size="sm" className="hidden sm:flex">
                <Phone className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="hidden sm:flex">
                <Video className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-2 sm:p-4">
          <div className="space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className="flex gap-2 sm:gap-3">
                {msg.type !== "system" && (
                  <Avatar className="w-6 h-6 sm:w-8 sm:h-8 flex-shrink-0">
                    <AvatarImage src={msg.avatar || "/placeholder.svg"} />
                    <AvatarFallback className="text-xs">
                      {msg.user
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                )}
                <div className={`flex-1 min-w-0 ${msg.type === "system" ? "text-center" : ""}`}>
                  {msg.type === "system" ? (
                    <div className="text-sm text-muted-foreground bg-muted rounded px-3 py-2 inline-block">
                      {msg.content}
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="font-semibold text-sm truncate">{msg.user}</span>
                        <span className="text-xs text-muted-foreground flex-shrink-0">{msg.timestamp}</span>
                        {msg.type === "alert" && (
                          <Badge variant="destructive" className="text-xs">
                            Alert
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-foreground break-words">{msg.content}</div>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Message Input */}
        <div className="p-2 sm:p-4 border-t border-border bg-card">
          <div className="flex gap-2">
            <Input
              placeholder={`Message #${selectedChannel}`}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              className="flex-1 text-sm"
            />
            <Button onClick={handleSendMessage} disabled={!message.trim()} size="sm">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
