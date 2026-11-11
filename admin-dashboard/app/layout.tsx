import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Café OS — Admin',
  description: 'Premium coffee shop ordering platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-amber-50 to-orange-50 text-amber-900">
        {children}
      </body>
    </html>
  )
}
