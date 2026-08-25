import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "ResearchAI — Enterprise Multi-Agent Research Platform",
  description: "Advanced AI-powered multi-agent research platform searching academic papers, medical journals, books, patents, and trusted sources.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-white text-gray-900 antialiased">
      <body className="min-h-screen bg-white font-sans text-gray-900">
        {children}
      </body>
    </html>
  );
}
