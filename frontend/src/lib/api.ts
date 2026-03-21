import type {
  Event,
  EventListResponse,
  EventFilters,
  Category,
  Venue,
  DailyPicks,
  ChatMessage,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
  if (filters?.neighborhood) params.set("neighborhood", filters.neighborhood);
  if (filters?.price_level) params.set("price_level", filters.price_level);
  if (filters?.venue) params.set("venue", filters.venue);
  if (filters?.search) params.set("search", filters.search);
  if (filters?.limit) params.set("limit", String(filters.limit));
  if (filters?.offset) params.set("offset", String(filters.offset));

  const query = params.toString();
  return fetchApi<EventListResponse>(
    `/cities/${city}/events${query ? `?${query}` : ""}`
  );
}

export async function getCategories(city: string): Promise<Category[]> {
  return fetchApi<Category[]>(`/cities/${city}/categories`);
}

export async function getVenues(city: string): Promise<Venue[]> {
  return fetchApi<Venue[]>(`/cities/${city}/venues`);
}

export async function getPicks(city: string): Promise<DailyPicks> {
  return fetchApi<DailyPicks>(`/cities/${city}/picks`);
}

export async function postChat(
  city: string,
  message: string
): Promise<ChatMessage> {
  return fetchApi<ChatMessage>(`/cities/${city}/chat`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
