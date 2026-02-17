import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@scaffold-ai/ui/globals.css";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scaffold AI",
  description: "Design full-stack applications with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
