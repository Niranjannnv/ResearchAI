import type { Metadata, Viewport } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "ResearchAI — Enterprise Multi-Agent Research Platform",
  description: "Advanced AI-powered multi-agent research platform searching academic papers, medical journals, books, patents, and trusted sources.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  viewportFit: "cover",
  themeColor: "#ffffff",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-white text-gray-900 antialiased overflow-x-hidden w-full">
      <body className="min-h-screen bg-white font-sans text-gray-900 overflow-x-hidden w-full">
        {children}
      </body>
    </html>
  );
}
