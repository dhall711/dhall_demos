import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Retail Analytics Dashboard",
  description: "Retail analytics powered by Fivetran + Snowflake Cortex AI",
  icons: { icon: "/icon.svg" },
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}
