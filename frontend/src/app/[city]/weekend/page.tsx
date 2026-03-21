"use client";

import { Sparkles, Calendar } from "lucide-react";

export default function WeekendPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Sparkles className="h-8 w-8 text-primary" />
          Weekend Planner
        </h1>
        <p className="text-muted-foreground mt-1">
          AI-curated plans for your perfect weekend
        </p>
      </div>

      {/* Weekend Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Saturday */}
        <div className="glass-strong rounded-2xl p-6 glow-purple">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Saturday</h2>
          </div>
          <div className="space-y-3">
            {["Morning", "Afternoon", "Evening"].map((timeSlot) => (
              <div
                key={timeSlot}
                className="glass-subtle rounded-lg p-4 space-y-2"
              >
                <p className="text-xs font-medium text-primary uppercase tracking-wider">
                  {timeSlot}
                </p>
                <p className="text-muted-foreground text-sm animate-pulse">
                  Coming soon...
                </p>
              </div>
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
            {["Morning", "Afternoon", "Evening"].map((timeSlot) => (
              <div
                key={timeSlot}
                className="glass-subtle rounded-lg p-4 space-y-2"
              >
                <p className="text-xs font-medium text-primary uppercase tracking-wider">
                  {timeSlot}
                </p>
                <p className="text-muted-foreground text-sm animate-pulse">
                  Coming soon...
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Weekend Highlights */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Weekend Highlights</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass rounded-xl p-5 space-y-3">
              <div className="w-full h-32 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-glow/10 flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-muted-foreground/30 animate-pulse" />
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
