"use client";

import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import {
  Home,
  Music,
  UtensilsCrossed,
  CalendarDays,
  Trophy,
  Wine,
  Sparkles,
  MessageCircle,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { label: "Home", icon: Home, path: "" },
  { label: "Concerts & Music", icon: Music, path: "/concerts" },
  { label: "Restaurants", icon: UtensilsCrossed, path: "/restaurants" },
  { label: "Activities", icon: CalendarDays, path: "/activities" },
  { label: "Sports", icon: Trophy, path: "/sports" },
  { label: "Nightlife", icon: Wine, path: "/nightlife" },
  { label: "Weekend Planner", icon: Sparkles, path: "/weekend" },
  { label: "Ask What2Do", icon: MessageCircle, path: "/chat" },
];

export function CityLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const city = params.city as string;
  const cityDisplay = city.charAt(0).toUpperCase() + city.slice(1);
  const [mobileOpen, setMobileOpen] = useState(false);

  function isActive(itemPath: string) {
    const fullPath = `/${city}${itemPath}`;
    if (itemPath === "") {
      return pathname === `/${city}` || pathname === `/${city}/`;
    }
    return pathname.startsWith(fullPath);
  }

  return (
    <div className="flex min-h-screen">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 glass-strong z-40">
        <div className="flex flex-col h-full px-4 py-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-primary glow-purple inline-block">
              What2Do
            </h1>
            <p className="text-sm text-muted-foreground mt-1">{cityDisplay}</p>
          </div>

          <nav className="flex-1 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  href={`/${city}${item.path}`}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? "glass bg-accent text-accent-foreground glow-purple"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass-strong px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold text-primary">What2Do</h1>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg hover:bg-accent/50 transition-colors"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40 pt-16">
          <div
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <nav className="relative glass-strong mx-4 mt-2 p-4 rounded-xl space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  href={`/${city}${item.path}`}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? "glass bg-accent text-accent-foreground glow-purple"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      )}

      {/* Mobile Bottom Nav */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 glass-strong safe-bottom">
        <nav className="flex items-center justify-around px-2 py-2">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                href={`/${city}${item.path}`}
                className={`flex flex-col items-center gap-1 px-2 py-1.5 rounded-lg text-xs transition-all ${
                  active
                    ? "text-primary"
                    : "text-muted-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="truncate max-w-[60px]">
                  {item.label.split(" ")[0]}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 pt-16 lg:pt-0 pb-20 lg:pb-0">
        <div className="p-6 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
