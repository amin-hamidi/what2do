"use client";

import { Suspense } from "react";
import { UtensilsCrossed } from "lucide-react";
import { EventFilters, type FilterConfig } from "@/components/events/event-filters";
import { EventFeed } from "@/components/events/event-feed";

const filters: FilterConfig[] = [
  {
    key: "cuisine_type",
    label: "Cuisine",
    options: [
      { value: "mexican", label: "Mexican" },
      { value: "italian", label: "Italian" },
      { value: "japanese", label: "Japanese" },
      { value: "korean", label: "Korean" },
      { value: "thai", label: "Thai" },
      { value: "american", label: "American" },
      { value: "bbq", label: "BBQ" },
      { value: "seafood", label: "Seafood" },
      { value: "indian", label: "Indian" },
      { value: "mediterranean", label: "Mediterranean" },
    ],
  },
  {
    key: "neighborhood",
    label: "Neighborhood",
    options: [
      { value: "Deep Ellum", label: "Deep Ellum" },
      { value: "Bishop Arts", label: "Bishop Arts" },
      { value: "Uptown", label: "Uptown" },
      { value: "Downtown", label: "Downtown" },
      { value: "Knox-Henderson", label: "Knox-Henderson" },
      { value: "Lower Greenville", label: "Lower Greenville" },
      { value: "Lakewood", label: "Lakewood" },
      { value: "Oak Cliff", label: "Oak Cliff" },
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

export default function RestaurantsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <UtensilsCrossed className="h-8 w-8 text-primary" />
          Restaurants
        </h1>
        <p className="text-muted-foreground mt-1">
          Discover new restaurants, openings, and must-try spots
        </p>
      </div>
      <Suspense>
        <EventFilters filters={filters} />
        <EventFeed category="restaurants" />
      </Suspense>
    </div>
  );
}
