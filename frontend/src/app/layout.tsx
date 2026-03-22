import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#8B5CF6",
};

export const metadata: Metadata = {
  title: {
    default: "What2Do | Dallas Events & Activities",
    template: "%s | What2Do",
  },
  description:
    "AI-powered event finder for Dallas, TX. Discover concerts, restaurants, nightlife, sports, and activities curated just for you.",
  keywords: [
    "Dallas events",
    "things to do in Dallas",
    "Dallas concerts",
    "Dallas restaurants",
    "Dallas nightlife",
    "Dallas activities",
    "Dallas sports",
  ],
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "What2Do",
    title: "What2Do | Dallas Events & Activities",
    description:
      "AI-powered event finder for Dallas, TX. Discover concerts, restaurants, nightlife, sports, and activities.",
  },
  twitter: {
    card: "summary_large_image",
    title: "What2Do | Dallas Events & Activities",
    description: "AI-powered event finder for Dallas, TX.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
      >
        <div className="fixed inset-0 bg-mesh pointer-events-none" />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
