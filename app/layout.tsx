import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Operations Dashboard",
  description: "Monitor agent activity, token usage, and system health",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
