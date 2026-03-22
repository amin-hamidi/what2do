"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Loader2, SearchX } from "lucide-react";
import { getEvents } from "@/lib/api";
import { EventCard } from "./event-card";
import type { Event, EventFilters } from "@/lib/types";

interface EventFeedProps {
  category?: string;
  limit?: number;
}

function SkeletonCard() {
  return (
    <div className="glass rounded-xl overflow-hidden animate-pulse">
      <div className="w-full h-44 bg-gradient-to-br from-primary/8 to-cyan-glow/8" />
      <div className="p-4 space-y-3">
        <div className="h-4 w-3/4 rounded bg-muted/60" />
        <div className="h-3 w-full rounded bg-muted/40" />
        <div className="h-3 w-1/2 rounded bg-muted/40" />
        <div className="flex gap-2 pt-1">
          <div className="h-5 w-14 rounded bg-muted/30" />
          <div className="h-5 w-10 rounded bg-muted/30" />
        </div>
      </div>
    </div>
  );
}

export function EventFeed({ category, limit = 18 }: EventFeedProps) {
  const params = useParams();
  const searchParams = useSearchParams();
  const city = params.city as string;

  const [events, setEvents] = useState<Event[]>([]);
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  const sentinelRef = useRef<HTMLDivElement>(null);
  const fetchIdRef = useRef(0);

  // Build filters from URL search params
  const buildFilters = useCallback((): EventFilters => {
    const filters: EventFilters = { limit };
    if (category) filters.category = category;
    const q = searchParams.get("q");
    if (q) filters.q = q;
    const neighborhood = searchParams.get("neighborhood");
    if (neighborhood) filters.neighborhood = neighborhood;
    const genre = searchParams.get("genre");
    if (genre) filters.genre = genre;
    const cuisine_type = searchParams.get("cuisine_type");
    if (cuisine_type) filters.cuisine_type = cuisine_type;
    const price_level = searchParams.get("price_level");
    if (price_level) filters.price_level = price_level;
    const venue_id = searchParams.get("venue_id");
    if (venue_id) filters.venue_id = venue_id;
    const tags = searchParams.get("tags");
    if (tags) filters.tags = tags;
    const date_from = searchParams.get("date_from");
    if (date_from) filters.date_from = date_from;
    const date_to = searchParams.get("date_to");
    if (date_to) filters.date_to = date_to;
    return filters;
  }, [category, limit, searchParams]);

  // Initial load + filter changes
  useEffect(() => {
    const id = ++fetchIdRef.current;
    setLoading(true);
    setEvents([]);
    setCursor(undefined);
    setHasMore(true);

    const filters = buildFilters();

    getEvents(city, filters)
      .then((res) => {
        if (id !== fetchIdRef.current) return;
        setEvents(res.items);
        setCursor(res.cursor ?? undefined);
        setHasMore(!!res.cursor);
        setTotal(res.total);
      })
      .catch((err) => {
        if (id !== fetchIdRef.current) return;
        console.error("Failed to fetch events:", err);
      })
      .finally(() => {
        if (id === fetchIdRef.current) setLoading(false);
      });
  }, [city, buildFilters]);

  // Load more
  const loadMore = useCallback(() => {
    if (loadingMore || !hasMore || !cursor) return;
    setLoadingMore(true);

    const filters = buildFilters();
    filters.cursor = cursor;

    getEvents(city, filters)
      .then((res) => {
        setEvents((prev) => [...prev, ...res.items]);
        setCursor(res.cursor ?? undefined);
        setHasMore(!!res.cursor);
      })
      .catch((err) => console.error("Failed to load more:", err))
      .finally(() => setLoadingMore(false));
  }, [city, cursor, hasMore, loadingMore, buildFilters]);

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { rootMargin: "200px" }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [loadMore]);

  // Initial loading skeleton
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // Empty state
  if (events.length === 0) {
    return (
      <div className="glass rounded-2xl p-12 flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 rounded-2xl glass-strong glow-cyan flex items-center justify-center mb-4">
          <SearchX className="h-7 w-7 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-1">No events found</h3>
        <p className="text-muted-foreground text-sm max-w-md">
          Try adjusting your filters or check back later for new events.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted-foreground">
        {total} event{total !== 1 ? "s" : ""} found
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {events.map((event) => (
          <EventCard
            key={event.id}
            title={event.title}
            description={event.description}
            imageUrl={event.image_url}
            sourceUrl={event.source_url}
            date={event.starts_at}
            venue={event.venue_name}
            neighborhood={event.neighborhood}
            priceLevel={event.price_level}
            category={event.category_name}
            tags={event.tags ? event.tags.split(",") : undefined}
          />
        ))}
      </div>

      {/* Sentinel for infinite scroll */}
      <div ref={sentinelRef} className="h-4" />

      {/* Loading more indicator */}
      {loadingMore && (
        <div className="flex justify-center py-6">
          <Loader2 className="h-5 w-5 text-primary animate-spin" />
        </div>
      )}
    </div>
  );
}
