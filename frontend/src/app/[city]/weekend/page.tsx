"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Sparkles, Calendar, ExternalLink } from "lucide-react";
import { EventFeed } from "@/components/events/event-feed";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { getPicks } from "@/lib/api";
import type { AIPick } from "@/lib/types";

const TIME_SLOTS = ["Morning", "Afternoon", "Evening"];

const filters: FilterConfig[] = [
  {
    key: "tags",
    label: "Type",
    options: [
      { value: "festival", label: "Festivals" },
      { value: "outdoor", label: "Outdoor" },
      { value: "family", label: "Family-Friendly" },
      { value: "food", label: "Food & Drink" },
      { value: "live-music", label: "Live Music" },
      { value: "market", label: "Markets" },
    ],
  },
  {
    key: "price_level",
    label: "Price",
    options: [
      { value: "free", label: "Free" },
      { value: "$", label: "$" },
      { value: "$$", label: "$$" },
      { value: "$$$", label: "$$$" },
    ],
  },
];

function ItinerarySlot({ pick, slot }: { pick?: AIPick; slot: string }) {
  const event = pick?.event;
  return (
    <div className="glass-subtle rounded-lg p-4 space-y-2">
      <p className="text-xs font-medium text-primary uppercase tracking-wider">
        {slot}
      </p>
      {event ? (
        <div className="space-y-1">
          <h4 className="font-semibold text-sm">{event.title}</h4>
          <p className="text-muted-foreground text-xs">{pick?.ai_blurb}</p>
          {event.source_url && (
            <a
              href={event.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              Details <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">
          No curated pick yet
        </p>
      )}
    </div>
  );
}

export default function WeekendPage() {
  const params = useParams();
  const city = params.city as string;
  const [saturdayPicks, setSaturdayPicks] = useState<AIPick[]>([]);
  const [sundayPicks, setSundayPicks] = useState<AIPick[]>([]);

  useEffect(() => {
    getPicks(city)
      .then((data) => {
        const cats = (data as { categories: Record<string, AIPick[]> }).categories || {};
        setSaturdayPicks(cats["weekend_saturday"] || []);
        setSundayPicks(cats["weekend_sunday"] || []);
      })
      .catch(() => {});
  }, [city]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Sparkles className="h-8 w-8 text-primary" />
          Weekend Planner
        </h1>
        <p className="text-muted-foreground mt-1">
          AI-curated plans for your perfect weekend
        </p>
      </div>

      {/* AI Itinerary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Saturday */}
        <div className="glass-strong rounded-2xl p-6 glow-purple">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Saturday</h2>
          </div>
          <div className="space-y-3">
            {TIME_SLOTS.map((slot, i) => (
              <ItinerarySlot
                key={slot}
                slot={slot}
                pick={saturdayPicks[i]}
              />
            ))}
          </div>
        </div>

        {/* Sunday */}
        <div className="glass-strong rounded-2xl p-6 glow-cyan">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="h-5 w-5 text-cyan-glow" />
            <h2 className="text-lg font-semibold">Sunday</h2>
          </div>
          <div className="space-y-3">
            {TIME_SLOTS.map((slot, i) => (
              <ItinerarySlot
                key={slot}
                slot={slot}
                pick={sundayPicks[i]}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Weekend Events Feed */}
      <section>
        <h2 className="text-lg font-semibold mb-4">All Weekend Events</h2>
        <Suspense>
          <EventFilters filters={filters} />
          <EventFeed category="weekend" />
        </Suspense>
      </section>
    </div>
  );
}
