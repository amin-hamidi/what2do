"use client";

import { useParams } from "next/navigation";
import { RefreshCw, Sparkles, Clock, Moon, Calendar, UtensilsCrossed } from "lucide-react";
import { useState } from "react";

const widgetCards = [
  { title: "Happening Now", icon: Clock, color: "glow-cyan" },
  { title: "Tonight", icon: Moon, color: "glow-purple" },
  { title: "This Weekend", icon: Calendar, color: "glow-cyan" },
  { title: "New Restaurants", icon: UtensilsCrossed, color: "glow-purple" },
];

export default function CityHomePage() {
  const params = useParams();
  const city = params.city as string;
  const cityDisplay = city.charAt(0).toUpperCase() + city.slice(1);
  const [refreshing, setRefreshing] = useState(false);

  function handleRefresh() {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            What&apos;s happening in{" "}
            <span className="text-primary">{cityDisplay}</span>
          </h1>
          <p className="text-muted-foreground mt-1">
            Your AI-powered guide to the best events and activities
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="p-2.5 rounded-xl glass hover:glow-purple transition-all duration-300"
        >
          <RefreshCw
            className={`h-5 w-5 text-muted-foreground ${
              refreshing ? "animate-spin" : ""
            }`}
          />
        </button>
      </div>

      {/* Today's Top Pick */}
      <section>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Today&apos;s Top Pick
        </h2>
        <div className="glass-strong rounded-2xl p-6 glow-purple">
          <div className="flex items-center gap-6">
            <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-primary/30 to-cyan-glow/30 flex items-center justify-center shrink-0">
              <Sparkles className="h-10 w-10 text-primary animate-pulse" />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium text-primary uppercase tracking-wider">
                AI Pick of the Day
              </p>
              <h3 className="text-xl font-bold">Coming soon...</h3>
              <p className="text-muted-foreground text-sm">
                Our AI is learning about {cityDisplay}&apos;s best events.
                Check back soon for personalized recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Widget Grid */}
      <section>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {widgetCards.map((widget) => {
            const Icon = widget.icon;
            return (
              <div
                key={widget.title}
                className={`glass rounded-xl p-5 hover:${widget.color} transition-all duration-300 cursor-pointer group`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon className="h-4 w-4 text-primary" />
                  </div>
                  <h3 className="font-semibold text-sm">{widget.title}</h3>
                </div>
                <p className="text-muted-foreground text-xs animate-pulse">
                  Coming soon...
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Recommended for You */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recommended for You</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="glass rounded-xl p-5 space-y-3"
            >
              <div className="w-full h-32 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-glow/10 flex items-center justify-center">
                <span className="text-muted-foreground text-xs animate-pulse">
                  Coming soon...
                </span>
              </div>
              <div className="space-y-2">
                <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
                <div className="h-3 w-1/2 rounded bg-muted animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
