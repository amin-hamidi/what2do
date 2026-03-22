"use client";

import { Suspense } from "react";
import { Trophy } from "lucide-react";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { EventFeed } from "@/components/events/event-feed";

const filters: FilterConfig[] = [
  {
    key: "genre",
    label: "League",
    options: [
      { value: "NBA", label: "NBA (Mavericks)" },
      { value: "NFL", label: "NFL (Cowboys)" },
      { value: "NHL", label: "NHL (Stars)" },
      { value: "MLB", label: "MLB (Rangers)" },
      { value: "MLS", label: "MLS (FC Dallas)" },
    ],
  },
  {
    key: "neighborhood",
    label: "Venue Area",
    options: [
      { value: "Victory Park", label: "Victory Park (AAC)" },
      { value: "Arlington", label: "Arlington (AT&T / Globe Life)" },
      { value: "Frisco", label: "Frisco (Toyota Stadium)" },
    ],
  },
  {
    key: "price_level",
    label: "Price",
    options: [
      { value: "$", label: "$" },
      { value: "$$", label: "$$" },
      { value: "$$$", label: "$$$" },
      { value: "$$$$", label: "$$$$" },
    ],
  },
];

export default function SportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Trophy className="h-8 w-8 text-primary" />
          Sports
        </h1>
        <p className="text-muted-foreground mt-1">
          Games, matches, and sporting events in the area
        </p>
      </div>
      <Suspense>
        <EventFilters filters={filters} />
        <EventFeed category="sports" />
      </Suspense>
    </div>
  );
}
