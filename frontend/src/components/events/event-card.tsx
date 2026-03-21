"use client";

import { ExternalLink, MapPin, Clock, DollarSign } from "lucide-react";
import { formatDate, formatTime, formatPrice } from "@/lib/utils";

interface EventCardProps {
  title: string;
  description?: string;
  imageUrl?: string;
  sourceUrl?: string;
  date?: string;
  venue?: string;
  neighborhood?: string;
  priceLevel?: string;
  category?: string;
  tags?: string[];
}

export function EventCard({
  title,
  description,
  imageUrl,
  sourceUrl,
  date,
  venue,
  neighborhood,
  priceLevel,
  category,
  tags,
}: EventCardProps) {
  return (
    <div className="glass rounded-xl overflow-hidden group hover:glow-purple transition-all duration-300">
      {/* Image */}
      <div className="relative w-full h-44 overflow-hidden">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-primary/20 to-cyan-glow/20 flex items-center justify-center">
            <span className="text-muted-foreground/50 text-sm">No image</span>
          </div>
        )}
        {category && (
          <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg glass text-xs font-medium">
            {category}
          </span>
        )}
        {priceLevel && (
          <span className="absolute top-3 right-3 px-2.5 py-1 rounded-lg glass text-xs font-medium">
            <DollarSign className="h-3 w-3 inline-block -mt-0.5" />
            {formatPrice(priceLevel)}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-sm leading-tight line-clamp-2">
          {title}
        </h3>

        {description && (
          <p className="text-muted-foreground text-xs line-clamp-2">
            {description}
          </p>
        )}

        <div className="flex flex-col gap-1.5 text-xs text-muted-foreground">
          {date && (
            <div className="flex items-center gap-1.5">
              <Clock className="h-3 w-3 shrink-0" />
              <span>
                {formatDate(date)} at {formatTime(date)}
              </span>
            </div>
          )}
          {(venue || neighborhood) && (
            <div className="flex items-center gap-1.5">
              <MapPin className="h-3 w-3 shrink-0" />
              <span className="truncate">
                {venue}
                {venue && neighborhood ? " - " : ""}
                {neighborhood}
              </span>
            </div>
          )}
        </div>

        {/* Tags */}
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Source Link */}
        {sourceUrl && (
          <div className="pt-2 border-t border-border">
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline"
            >
              View Source
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
