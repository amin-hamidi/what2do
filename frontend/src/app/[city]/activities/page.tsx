"use client";

import { Suspense } from "react";
import { CalendarDays } from "lucide-react";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { EventFeed } from "@/components/events/event-feed";

const filters: FilterConfig[] = [
  {
    key: "tags",
    label: "Type",
    options: [
      { value: "festival", label: "Festivals" },
      { value: "market", label: "Markets" },
      { value: "art", label: "Art & Culture" },
      { value: "outdoor", label: "Outdoor" },
      { value: "family", label: "Family-Friendly" },
      { value: "workshop", label: "Workshops" },
      { value: "comedy", label: "Comedy" },
      { value: "charity", label: "Charity" },
    ],
  },
  {
    key: "neighborhood",
    label: "Area",
    options: [
      { value: "Deep Ellum", label: "Deep Ellum" },
      { value: "Downtown", label: "Downtown" },
      { value: "Uptown", label: "Uptown" },
      { value: "Bishop Arts", label: "Bishop Arts" },
      { value: "Fair Park", label: "Fair Park" },
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

export default function ActivitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <CalendarDays className="h-8 w-8 text-primary" />
          Activities
        </h1>
        <p className="text-muted-foreground mt-1">
          Things to do, festivals, markets, and experiences
        </p>
      </div>
      <Suspense>
        <EventFilters filters={filters} />
        <EventFeed category="activities" />
      </Suspense>
    </div>
  );
}
