"use client";

import { CalendarDays } from "lucide-react";

const filters = ["Type", "Date", "Indoor/Outdoor", "Family-Friendly"];

export default function ActivitiesPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <CalendarDays className="h-8 w-8 text-primary" />
          Activities
        </h1>
        <p className="text-muted-foreground mt-1">
          Things to do, festivals, markets, and experiences
        </p>
      </div>

      {/* Filter Bar */}
      <div className="glass rounded-xl p-4 flex flex-wrap gap-3">
        {filters.map((filter) => (
          <button
            key={filter}
            className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            {filter}
          </button>
        ))}
      </div>

      {/* Activity Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glass rounded-xl p-5 space-y-3">
            <div className="w-full h-40 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-glow/10 flex items-center justify-center">
              <CalendarDays className="h-8 w-8 text-muted-foreground/30" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
              <div className="h-3 w-1/2 rounded bg-muted animate-pulse" />
              <div className="h-3 w-1/3 rounded bg-muted animate-pulse" />
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      <div className="flex justify-center">
        <button className="px-6 py-2.5 rounded-xl glass hover:glow-purple transition-all duration-300 text-sm font-medium">
          Load more
        </button>
      </div>
    </div>
  );
}
