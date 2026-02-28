import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/lib/auth-context'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AutoUploader — AI Video Clip Agent',
  description: 'AI-powered clip generation, editing, and auto-posting to TikTok, Instagram, YouTube Shorts, and Facebook.',
  keywords: 'AI clips, auto post, TikTok, YouTube Shorts, Instagram Reels, video automation',
  openGraph: {
    title: 'AutoUploader — AI Video Clip Agent',
    description: 'Turn long videos into viral short-form clips automatically',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
