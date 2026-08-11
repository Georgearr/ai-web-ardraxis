import type { Metadata } from "next"
import "./globals.css"
import { Header } from "@/components/layout/Header"
import { Footer } from "@/components/layout/Footer"

export const metadata: Metadata = {
  title: "DRAX - Digital Resource Assistant of ARDRAXIS",
  description:
    "Empowering Information, Igniting Innovation. AI Assistant resmi untuk OSIS SMA Ignatius Global School.",
  icons: {
    icon: "/favicon.ico",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className="bg-ardraxis-dark min-h-screen antialiased">
        <div className="flex min-h-dvh flex-col">
          <Header />
          <main className="flex min-h-0 flex-1 flex-col">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  )
}
