"use client";

import { useParams } from "next/navigation";
import {
  RefreshCw,
  Sparkles,
  Clock,
  Moon,
  Calendar,
  UtensilsCrossed,
  LayoutGrid,
  CalendarDays,
  ExternalLink,
} from "lucide-react";
import { Suspense, useCallback, useEffect, useState } from "react";
import { triggerSync, getPicks, getEvents } from "@/lib/api";
import { EventFeed } from "@/components/events/event-feed";
import { EventCalendar } from "@/components/events/event-calendar";
import { cn } from "@/lib/utils";
import type { Event } from "@/lib/types";

interface PickData {
  top_pick?: {
    id: string;
    event_id: string;
    pick_type: string;
    rank: number;
    ai_blurb: string;
    event?: Event;
  };
  categories: Record<string, { ai_blurb: string; event?: Event }[]>;
}

interface WidgetData {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  count: number;
  preview?: string;
  color: string;
}

export default function CityHomePage() {
  const params = useParams();
  const city = params.city as string;
  const cityDisplay = city.charAt(0).toUpperCase() + city.slice(1);
  const [refreshing, setRefreshing] = useState(false);
  const [view, setView] = useState<"feed" | "calendar">("feed");
  const [feedKey, setFeedKey] = useState(0);
  const [picks, setPicks] = useState<PickData | null>(null);
  const [widgets, setWidgets] = useState<WidgetData[]>([]);

  // Fetch picks
  useEffect(() => {
    getPicks(city)
      .then((data) => setPicks(data as unknown as PickData))
      .catch(() => {});
  }, [city]);

  // Fetch widget data
  useEffect(() => {
    const now = new Date();
    const today = now.toISOString().split("T")[0];

    // Get next Saturday/Sunday
    const dayOfWeek = now.getDay();
    const daysUntilSat = (6 - dayOfWeek + 7) % 7 || 7;
    const saturday = new Date(now);
    saturday.setDate(now.getDate() + daysUntilSat);
    const sunday = new Date(saturday);
    sunday.setDate(saturday.getDate() + 1);
    const satStr = saturday.toISOString().split("T")[0];
    const sunStr = sunday.toISOString().split("T")[0];

    Promise.allSettled([
      // Tonight: events today
      getEvents(city, { date_from: today, date_to: today, limit: 5 }),
      // This Weekend
      getEvents(city, { date_from: satStr, date_to: sunStr, limit: 5 }),
      // New Restaurants (last 7 days)
      getEvents(city, { category: "restaurants", limit: 5 }),
    ]).then(([tonightRes, weekendRes, restaurantRes]) => {
      const tonight = tonightRes.status === "fulfilled" ? tonightRes.value : null;
      const weekend = weekendRes.status === "fulfilled" ? weekendRes.value : null;
      const restaurants = restaurantRes.status === "fulfilled" ? restaurantRes.value : null;

      setWidgets([
        {
          title: "Tonight",
          icon: Moon,
          count: tonight?.total ?? 0,
          preview: tonight?.items?.[0]?.title,
          color: "glow-purple",
        },
        {
          title: "This Weekend",
          icon: Calendar,
          count: weekend?.total ?? 0,
          preview: weekend?.items?.[0]?.title,
          color: "glow-cyan",
        },
        {
          title: "New Restaurants",
          icon: UtensilsCrossed,
          count: restaurants?.total ?? 0,
          preview: restaurants?.items?.[0]?.title,
          color: "glow-purple",
        },
      ]);
    });
  }, [city]);

  async function handleRefresh() {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await triggerSync(city, "dallasites101");
      setTimeout(() => {
        setFeedKey((k) => k + 1);
        setRefreshing(false);
      }, 3000);
    } catch (err) {
      console.error("Sync failed:", err);
      setRefreshing(false);
    }
  }

  const topPick = picks?.top_pick;
  const topEvent = topPick?.event;

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
        <div className="flex items-center gap-2">
          <div className="glass rounded-lg p-1 flex">
            <button
              onClick={() => setView("feed")}
              className={cn(
                "p-2 rounded-md transition-all",
                view === "feed"
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setView("calendar")}
              className={cn(
                "p-2 rounded-md transition-all",
                view === "calendar"
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <CalendarDays className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-2.5 rounded-xl glass hover:glow-purple transition-all duration-300 disabled:opacity-50"
          >
            <RefreshCw
              className={cn(
                "h-5 w-5 text-muted-foreground",
                refreshing && "animate-spin"
              )}
            />
          </button>
        </div>
      </div>

      {view === "calendar" ? (
        <Suspense>
          <EventCalendar />
        </Suspense>
      ) : (
        <>
          {/* Today's Top Pick */}
          <section>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Today&apos;s Top Pick
            </h2>
            <div className="glass-strong rounded-2xl p-6 glow-purple">
              <div className="flex items-center gap-6">
                <div className="w-32 h-32 rounded-xl bg-gradient-to-br from-primary/30 to-cyan-glow/30 flex items-center justify-center shrink-0 overflow-hidden">
                  {topEvent?.image_url ? (
                    <img
                      src={topEvent.image_url}
                      alt={topEvent.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <Sparkles className="h-10 w-10 text-primary animate-pulse" />
                  )}
                </div>
                <div className="space-y-2 min-w-0">
                  <p className="text-xs font-medium text-primary uppercase tracking-wider">
                    AI Pick of the Day
                  </p>
                  {topEvent ? (
                    <>
                      <h3 className="text-xl font-bold truncate">{topEvent.title}</h3>
                      <p className="text-muted-foreground text-sm line-clamp-2">
                        {topPick?.ai_blurb || topEvent.description}
                      </p>
                      {topEvent.source_url && (
                        <a
                          href={topEvent.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline"
                        >
                          View Event <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </>
                  ) : (
                    <>
                      <h3 className="text-xl font-bold">Coming soon...</h3>
                      <p className="text-muted-foreground text-sm">
                        Our AI is learning about {cityDisplay}&apos;s best events.
                        Check back soon for personalized recommendations.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </section>

          {/* Widget Grid */}
          <section>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {widgets.map((widget) => {
                const Icon = widget.icon;
                return (
                  <div
                    key={widget.title}
                    className={cn(
                      "glass rounded-xl p-5 transition-all duration-300 cursor-pointer group",
                      widget.count > 0 && `hover:${widget.color}`
                    )}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      <h3 className="font-semibold text-sm">{widget.title}</h3>
                      {widget.count > 0 && (
                        <span className="ml-auto text-xs text-primary font-medium">
                          {widget.count}
                        </span>
                      )}
                    </div>
                    {widget.preview ? (
                      <p className="text-muted-foreground text-xs truncate">
                        {widget.preview}
                      </p>
                    ) : (
                      <p className="text-muted-foreground text-xs">
                        No events yet
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          {/* Recent Events Feed */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Latest Events</h2>
            <Suspense>
              <EventFeed key={feedKey} />
            </Suspense>
          </section>
        </>
      )}
    </div>
  );
}
