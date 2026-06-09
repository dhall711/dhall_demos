import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "CRM Customer 360 Dashboard",
  description: "Financial Services Customer 360 powered by Fivetran + Snowflake Cortex AI",
  icons: { icon: "/icon.svg" },
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-[#0B1929]">{children}</body>
    </html>
  )
}
