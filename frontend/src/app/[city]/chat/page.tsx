"use client";

import { useParams } from "next/navigation";
import { MessageCircle, Send } from "lucide-react";
import { useRef, useState } from "react";
import { postChat } from "@/lib/api";
import { EventCard } from "@/components/events/event-card";
import type { Event } from "@/lib/types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  events?: Event[];
}

export default function ChatPage() {
  const params = useParams();
  const city = params.city as string;
  const cityDisplay = city.charAt(0).toUpperCase() + city.slice(1);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput("");
    setLoading(true);

    try {
      // Build history from previous messages
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await postChat(city, currentInput, history);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.message,
        events: response.events,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "Sorry, I had trouble connecting. Please try again in a moment.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      // Scroll to bottom
      setTimeout(() => {
        scrollRef.current?.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: "smooth",
        });
      }, 100);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-[calc(100dvh-8rem)] lg:h-[calc(100dvh-4rem)]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <MessageCircle className="h-8 w-8 text-primary" />
          Ask What2Do
        </h1>
        <p className="text-muted-foreground mt-1">
          Ask me anything about events and activities in {cityDisplay}
        </p>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="flex-1 flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl glass-strong glow-purple mx-auto flex items-center justify-center">
                <MessageCircle className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-lg font-semibold">
                  What are you looking for?
                </p>
                <p className="text-muted-foreground text-sm mt-1">
                  Try asking about concerts tonight, new restaurants, or weekend
                  plans
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center max-w-md">
                {[
                  "What concerts are this weekend?",
                  "Best new restaurants in Dallas",
                  "Fun date night ideas",
                  "Family activities this Saturday",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="px-3 py-1.5 rounded-lg glass text-xs text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className="space-y-3">
            <div
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "glass-strong"
                }`}
              >
                {message.content}
              </div>
            </div>

            {/* Show matched events for assistant messages */}
            {message.role === "assistant" &&
              message.events &&
              message.events.length > 0 && (
                <div className="pl-2">
                  <p className="text-xs text-muted-foreground mb-2">
                    Related events:
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {message.events.slice(0, 4).map((event) => (
                      <EventCard
                        key={event.id}
                        title={event.title}
                        description={event.description}
                        imageUrl={event.image_url}
                        sourceUrl={event.source_url}
                        date={event.starts_at}
                        venue={event.venue_name}
                        neighborhood={event.neighborhood}
                        priceLevel={event.price_level}
                        category={event.category_name}
                      />
                    ))}
                  </div>
                </div>
              )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="glass-strong rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="glass-strong rounded-2xl p-3 flex items-end gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask about events in ${cityDisplay}...`}
          rows={1}
          className="flex-1 bg-transparent border-0 outline-none resize-none text-sm placeholder:text-muted-foreground"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="p-2.5 rounded-xl bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
