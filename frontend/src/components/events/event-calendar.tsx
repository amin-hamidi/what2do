"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { getCalendarEvents } from "@/lib/api";
import { EventCard } from "./event-card";
import { cn } from "@/lib/utils";
import type { Event, CalendarEvents } from "@/lib/types";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

export function EventCalendar() {
  const params = useParams();
  const city = params.city as string;

  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [data, setData] = useState<CalendarEvents>({});
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const today = new Date();
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  const fetchData = useCallback(() => {
    setLoading(true);
    const dateFrom = `${year}-${String(month + 1).padStart(2, "0")}-01`;
    const lastDay = getDaysInMonth(year, month);
    const dateTo = `${year}-${String(month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

    getCalendarEvents(city, dateFrom, dateTo)
      .then(setData)
      .catch((err) => console.error("Calendar fetch failed:", err))
      .finally(() => setLoading(false));
  }, [city, year, month]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const prevMonth = () => {
    if (month === 0) {
      setMonth(11);
      setYear((y) => y - 1);
    } else {
      setMonth((m) => m - 1);
    }
    setSelectedDate(null);
  };

  const nextMonth = () => {
    if (month === 11) {
      setMonth(0);
      setYear((y) => y + 1);
    } else {
      setMonth((m) => m + 1);
    }
    setSelectedDate(null);
  };

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  const monthName = new Date(year, month).toLocaleString("en-US", { month: "long" });

  const selectedEvents: Event[] = selectedDate ? (data[selectedDate] || []) : [];

  return (
    <div className="space-y-4">
      {/* Month Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={prevMonth}
          className="p-2 rounded-lg glass hover:glow-purple transition-all"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <h3 className="text-lg font-semibold">
          {monthName} {year}
        </h3>
        <button
          onClick={nextMonth}
          className="p-2 rounded-lg glass hover:glow-purple transition-all"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
        </div>
      ) : (
        <>
          {/* Calendar Grid */}
          <div className="glass rounded-xl p-3">
            {/* Weekday headers */}
            <div className="grid grid-cols-7 gap-1 mb-1">
              {WEEKDAYS.map((day) => (
                <div
                  key={day}
                  className="text-center text-xs font-medium text-muted-foreground py-2"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Day cells */}
            <div className="grid grid-cols-7 gap-1">
              {/* Empty cells for days before month starts */}
              {Array.from({ length: firstDay }).map((_, i) => (
                <div key={`empty-${i}`} className="aspect-square" />
              ))}

              {/* Day cells */}
              {Array.from({ length: daysInMonth }).map((_, i) => {
                const day = i + 1;
                const dateKey = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                const eventCount = (data[dateKey] || []).length;
                const isToday = dateKey === todayKey;
                const isSelected = dateKey === selectedDate;

                return (
                  <button
                    key={day}
                    onClick={() => setSelectedDate(isSelected ? null : dateKey)}
                    className={cn(
                      "aspect-square rounded-lg flex flex-col items-center justify-center gap-0.5 text-sm transition-all relative",
                      isToday && "ring-1 ring-primary",
                      isSelected
                        ? "glass-strong glow-purple text-primary font-semibold"
                        : eventCount > 0
                          ? "hover:glass-strong cursor-pointer"
                          : "text-muted-foreground/40"
                    )}
                  >
                    <span>{day}</span>
                    {eventCount > 0 && (
                      <div className="flex gap-0.5">
                        {eventCount <= 3 ? (
                          Array.from({ length: eventCount }).map((_, j) => (
                            <span
                              key={j}
                              className="w-1 h-1 rounded-full bg-primary"
                            />
                          ))
                        ) : (
                          <span className="text-[10px] text-primary font-medium">
                            {eventCount}
                          </span>
                        )}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selected date events */}
          {selectedDate && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-muted-foreground">
                {new Date(selectedDate + "T00:00:00").toLocaleDateString("en-US", {
                  weekday: "long",
                  month: "long",
                  day: "numeric",
                })}
                {" "}
                <span className="text-primary">
                  ({selectedEvents.length} event{selectedEvents.length !== 1 ? "s" : ""})
                </span>
              </h4>
              {selectedEvents.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedEvents.map((event) => (
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
              ) : (
                <div className="glass rounded-xl p-6 text-center">
                  <p className="text-muted-foreground text-sm">
                    No events scheduled for this day.
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
