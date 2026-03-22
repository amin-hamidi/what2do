"use client";

import { useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronDown, X, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterConfig {
  key: string;
  label: string;
  options: FilterOption[];
}

interface EventFiltersProps {
  filters: FilterConfig[];
  className?: string;
}

export function EventFilters({ filters, className }: EventFiltersProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const setParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
      // Reset cursor when filters change
      params.delete("cursor");
      router.push(`?${params.toString()}`, { scroll: false });
    },
    [router, searchParams]
  );

  const clearAll = useCallback(() => {
    router.push("?", { scroll: false });
  }, [router]);

  const activeCount = filters.reduce(
    (count, f) => count + (searchParams.get(f.key) ? 1 : 0),
    0
  );

  const searchValue = searchParams.get("q") || "";

  return (
    <div className={cn("space-y-3", className)}>
      <div className="glass rounded-xl p-3 flex items-center gap-2 overflow-x-auto scrollbar-none">
        {/* Search input */}
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
          <input
            type="text"
            placeholder="Search events..."
            defaultValue={searchValue}
            onChange={(e) => {
              const val = e.target.value;
              if (searchTimer.current) clearTimeout(searchTimer.current);
              searchTimer.current = setTimeout(() => setParam("q", val), 400);
            }}
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-secondary/60 border border-glass-border text-sm placeholder:text-muted-foreground/60 outline-none focus:ring-1 focus:ring-primary/40 transition-all"
          />
        </div>

        {/* Filter dropdowns */}
        {filters.map((filter) => {
          const currentValue = searchParams.get(filter.key) || "";
          return (
            <div key={filter.key} className="relative group">
              <select
                value={currentValue}
                onChange={(e) => setParam(filter.key, e.target.value)}
                className={cn(
                  "appearance-none pl-3 pr-8 py-2 rounded-lg text-sm font-medium cursor-pointer outline-none transition-all",
                  "border border-glass-border",
                  currentValue
                    ? "bg-primary/15 text-primary border-primary/30"
                    : "bg-secondary/60 text-secondary-foreground hover:bg-secondary/80"
                )}
              >
                <option value="">{filter.label}</option>
                {filter.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
            </div>
          );
        })}

        {/* Clear all */}
        {activeCount > 0 && (
          <button
            onClick={clearAll}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors"
          >
            <X className="h-3 w-3" />
            Clear ({activeCount})
          </button>
        )}
      </div>
    </div>
  );
}
