export interface Event {
  id: string;
  city_id: string;
  category_id: string;
  venue_id?: string;
  source_id: string;
  title: string;
  slug: string;
  description?: string;
  short_description?: string;
  image_url?: string;
  source_url: string;
  starts_at?: string;
  ends_at?: string;
  is_all_day: boolean;
  tags?: string;
  price_level?: string;
  price_min?: number;
  price_max?: number;
  genre?: string;
  cuisine_type?: string;
  neighborhood?: string;
  status: string;
  content_hash: string;
  created_at: string;
  scraped_at: string;
  venue_name?: string;
  category_name?: string;
  source_name?: string;
}

export interface EventListResponse {
  items: Event[];
  total: number;
  cursor?: string;
}

export interface EventFilters {
  category?: string;
  date_from?: string;
  date_to?: string;
  venue_id?: string;
  neighborhood?: string;
  genre?: string;
  cuisine_type?: string;
  price_level?: string;
  tags?: string;
  q?: string;
  cursor?: string;
  limit?: number;
}

export interface City {
  id: string;
  slug: string;
  name: string;
  state: string;
  timezone: string;
  is_active: boolean;
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  icon?: string;
  sort_order: number;
  event_count?: number;
}

export interface Venue {
  id: string;
  city_id: string;
  name: string;
  slug: string;
  address?: string;
  neighborhood?: string;
  website_url?: string;
  venue_type?: string;
  event_count?: number;
}

export interface Source {
  id: string;
  name: string;
  source_type: string;
  is_active: boolean;
  last_scraped_at?: string;
}

export interface AIPick {
  id: string;
  event_id: string;
  pick_date: string;
  pick_type: string;
  rank: number;
  ai_blurb: string;
  event?: Event;
}

export interface DailyPicks {
  top_pick?: AIPick;
  categories: Record<string, AIPick[]>;
}

export interface ChatResponse {
  message: string;
  events: Event[];
}

export interface SyncTriggerResponse {
  task_id: string;
  source: string;
  status: string;
}

export type CalendarEvents = Record<string, Event[]>;
