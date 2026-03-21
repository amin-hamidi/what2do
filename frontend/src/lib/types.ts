export interface Event {
  id: string;
  title: string;
  description?: string;
  image_url?: string;
  source_url?: string;
  date?: string;
  end_date?: string;
  venue?: string;
  address?: string;
  neighborhood?: string;
  city: string;
  price_level?: string;
  price_min?: number;
  price_max?: number;
  category: string;
  tags?: string[];
  source: string;
  created_at: string;
  updated_at: string;
}

export interface EventListResponse {
  events: Event[];
  total: number;
  limit: number;
  offset: number;
}

export interface EventFilters {
  category?: string;
  date_from?: string;
  date_to?: string;
  neighborhood?: string;
  price_level?: string;
  venue?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface City {
  slug: string;
  name: string;
  state: string;
  timezone: string;
  enabled: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  event_count: number;
}

export interface Venue {
  id: string;
  name: string;
  address?: string;
  neighborhood?: string;
  city: string;
  lat?: number;
  lng?: number;
}

export interface Source {
  id: string;
  name: string;
  slug: string;
  url: string;
  scraper_type: string;
  enabled: boolean;
  last_scraped?: string;
}

export interface AIPick {
  id: string;
  event: Event;
  reason: string;
  rank: number;
}

export interface DailyPicks {
  date: string;
  city: string;
  top_pick: AIPick;
  picks: AIPick[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  events?: Event[];
  created_at: string;
}
