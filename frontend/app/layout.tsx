import type { Metadata } from "next";
import { Kanit, Sarabun } from "next/font/google";
import "./globals.css";

const bodyFont = Sarabun({
  variable: "--font-body",
  subsets: ["latin", "thai"],
  weight: ["300", "400", "500", "600", "700"],
});

const displayFont = Kanit({
  variable: "--font-display",
  subsets: ["latin", "thai"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "True Home Dashboard",
  description: "Family dashboard and subscription assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${bodyFont.variable} ${displayFont.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
