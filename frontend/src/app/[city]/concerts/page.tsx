"use client";

import { Suspense } from "react";
import { Music } from "lucide-react";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { EventFeed } from "@/components/events/event-feed";

const filters: FilterConfig[] = [
  {
    key: "genre",
    label: "Genre",
    options: [
      { value: "rock", label: "Rock" },
      { value: "hip-hop", label: "Hip Hop" },
      { value: "country", label: "Country" },
      { value: "electronic", label: "Electronic" },
      { value: "jazz", label: "Jazz" },
      { value: "r&b", label: "R&B" },
      { value: "latin", label: "Latin" },
      { value: "indie", label: "Indie" },
      { value: "pop", label: "Pop" },
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
  {
    key: "neighborhood",
    label: "Area",
    options: [
      { value: "Deep Ellum", label: "Deep Ellum" },
      { value: "Victory Park", label: "Victory Park" },
      { value: "Design District", label: "Design District" },
      { value: "Uptown", label: "Uptown" },
      { value: "Downtown", label: "Downtown" },
      { value: "Arlington", label: "Arlington" },
    ],
  },
];

export default function ConcertsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Music className="h-8 w-8 text-primary" />
          Concerts & Music
        </h1>
        <p className="text-muted-foreground mt-1">
          Live music, concerts, and DJ sets happening near you
        </p>
      </div>
      <Suspense>
        <EventFilters filters={filters} />
        <EventFeed category="concerts" />
      </Suspense>
    </div>
  );
}
