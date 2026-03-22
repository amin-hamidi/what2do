import type { Metadata } from "next";
import { CityLayoutClient } from "./layout-client";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ city: string }>;
}): Promise<Metadata> {
  const { city } = await params;
  const cityDisplay = city.charAt(0).toUpperCase() + city.slice(1);
  return {
    title: {
      default: `${cityDisplay} Events & Activities`,
      template: `%s in ${cityDisplay} | What2Do`,
    },
    description: `Discover the best events, concerts, restaurants, and activities in ${cityDisplay}. AI-powered recommendations updated daily.`,
    openGraph: {
      title: `What2Do ${cityDisplay}`,
      description: `AI-powered event finder for ${cityDisplay}`,
    },
  };
}

export default function CityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <CityLayoutClient>{children}</CityLayoutClient>;
}
