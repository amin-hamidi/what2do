"use client";

import { Suspense } from "react";
import { Wine } from "lucide-react";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { EventFeed } from "@/components/events/event-feed";

const filters: FilterConfig[] = [
  {
    key: "tags",
    label: "Type",
    options: [
      { value: "bar", label: "Bars" },
      { value: "club", label: "Clubs" },
      { value: "lounge", label: "Lounges" },
      { value: "rooftop", label: "Rooftop" },
      { value: "cocktail", label: "Cocktail Bars" },
      { value: "live-music", label: "Live Music" },
      { value: "comedy", label: "Comedy" },
    ],
  },
  {
    key: "neighborhood",
    label: "Neighborhood",
    options: [
      { value: "Deep Ellum", label: "Deep Ellum" },
      { value: "Uptown", label: "Uptown" },
      { value: "Downtown", label: "Downtown" },
      { value: "Knox-Henderson", label: "Knox-Henderson" },
      { value: "Lower Greenville", label: "Lower Greenville" },
      { value: "Bishop Arts", label: "Bishop Arts" },
      { value: "Design District", label: "Design District" },
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
      { value: "$$$$", label: "$$$$" },
    ],
  },
];

export default function NightlifePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Wine className="h-8 w-8 text-primary" />
          Nightlife
        </h1>
        <p className="text-muted-foreground mt-1">
          Bars, clubs, and late-night spots worth checking out
        </p>
      </div>
      <Suspense>
        <EventFilters filters={filters} />
        <EventFeed category="nightlife" />
      </Suspense>
    </div>
  );
}
