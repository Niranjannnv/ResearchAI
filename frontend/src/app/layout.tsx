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
    <html lang="en" className="h-full w-full bg-white text-gray-900 antialiased overflow-hidden">
      <body className="h-full w-full bg-white font-sans text-gray-900 overflow-hidden fixed inset-0">
        {children}
      </body>
    </html>
  );
}
