import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AIOS Quantum - The Interface',
  description: 'Cube containing Sphere - The fundamental visualization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
