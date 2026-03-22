import type {
  Event,
  EventListResponse,
  EventFilters,
  Category,
  Venue,
  DailyPicks,
  ChatResponse,
  SyncTriggerResponse,
  CalendarEvents,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export async function getEvents(
  city: string,
  filters?: EventFilters
): Promise<EventListResponse> {
  const params = new URLSearchParams();
  if (filters?.category) params.set("category", filters.category);
  if (filters?.date_from) params.set("date_from", filters.date_from);
  if (filters?.date_to) params.set("date_to", filters.date_to);
  if (filters?.venue_id) params.set("venue_id", filters.venue_id);
  if (filters?.neighborhood) params.set("neighborhood", filters.neighborhood);
  if (filters?.genre) params.set("genre", filters.genre);
  if (filters?.cuisine_type) params.set("cuisine_type", filters.cuisine_type);
  if (filters?.price_level) params.set("price_level", filters.price_level);
  if (filters?.tags) params.set("tags", filters.tags);
  if (filters?.q) params.set("q", filters.q);
  if (filters?.cursor) params.set("cursor", filters.cursor);
  if (filters?.limit) params.set("limit", String(filters.limit));

  const query = params.toString();
  return fetchApi<EventListResponse>(
    `/${city}/events${query ? `?${query}` : ""}`
  );
}

export async function getCalendarEvents(
  city: string,
  dateFrom?: string,
  dateTo?: string
): Promise<CalendarEvents> {
  const params = new URLSearchParams();
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  const query = params.toString();
  return fetchApi<CalendarEvents>(
    `/${city}/events/calendar${query ? `?${query}` : ""}`
  );
}

export async function getCategories(city: string): Promise<Category[]> {
  return fetchApi<Category[]>(`/${city}/categories`);
}

export async function getVenues(city: string): Promise<Venue[]> {
  return fetchApi<Venue[]>(`/${city}/venues`);
}

export async function getPicks(city: string): Promise<DailyPicks> {
  return fetchApi<DailyPicks>(`/${city}/picks`);
}

export async function postChat(
  city: string,
  message: string,
  history?: { role: string; content: string }[]
): Promise<ChatResponse> {
  return fetchApi<ChatResponse>(`/${city}/chat`, {
    method: "POST",
    body: JSON.stringify({ message, history: history || [] }),
  });
}

export async function triggerSync(
  city: string,
  sourceName: string
): Promise<SyncTriggerResponse> {
  return fetchApi<SyncTriggerResponse>(`/${city}/sync/${sourceName}`, {
    method: "POST",
  });
}
