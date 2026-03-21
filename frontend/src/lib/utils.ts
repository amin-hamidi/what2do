import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string): string {
  const d = new Date(date);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export function formatTime(date: string): string {
  const d = new Date(date);
  return d.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatPrice(level: string): string {
  const map: Record<string, string> = {
    free: "Free",
    "$": "$",
    "$$": "$$",
    "$$$": "$$$",
    "$$$$": "$$$$",
    low: "$",
    medium: "$$",
    high: "$$$",
    premium: "$$$$",
  };
  return map[level.toLowerCase()] || level;
}
