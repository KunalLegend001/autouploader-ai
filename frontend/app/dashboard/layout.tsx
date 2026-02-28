'use client'

import { useAuth } from '@/lib/auth-context'
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useEffect } from 'react'

const NAV_ITEMS = [
    { href: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { href: '/dashboard/generate', label: 'Generate Clips', icon: '✂️' },
    { href: '/dashboard/clips', label: 'My Clips', icon: '🎬' },
    { href: '/dashboard/channels', label: 'Channels', icon: '📺' },
    { href: '/dashboard/posting', label: 'Auto-Post', icon: '📤' },
    { href: '/dashboard/analytics', label: 'Analytics', icon: '📊' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const { user, logout, isLoading } = useAuth()
    const pathname = usePathname()
    const router = useRouter()

    useEffect(() => {
        if (!isLoading && !user) {
            router.push('/login')
        }
    }, [user, isLoading, router])

    if (isLoading) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="spinner" style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--accent-purple)', borderRadius: '50%', margin: '0 auto 1rem' }} />
                    <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
                </div>
            </div>
        )
    }

    if (!user) return null

    return (
        <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
            {/* ── Sidebar ── */}
            <aside className="sidebar">
                {/* Logo */}
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{ width: 36, height: 36, borderRadius: '10px', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem' }}>🚀</div>
                        <div>
                            <div style={{ fontWeight: 700, fontSize: '1rem' }}>AutoUploader</div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>AI Video Agent</div>
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    {NAV_ITEMS.map(item => (
                        <Link key={item.href} href={item.href} style={{ textDecoration: 'none' }}>
                            <div className={`sidebar-link ${pathname === item.href ? 'active' : ''}`}>
                                <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
                                <span style={{ fontSize: '0.9rem' }}>{item.label}</span>
                            </div>
                        </Link>
                    ))}
                </nav>

                {/* User */}
                <div style={{ padding: '1rem', borderTop: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                        <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.9rem' }}>
                            {user.username[0].toUpperCase()}
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{user.username}</div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{user.plan} plan</div>
                        </div>
                    </div>
                    <button onClick={logout} className="btn-secondary" style={{ width: '100%', padding: '0.5rem', fontSize: '0.8rem', textAlign: 'center' }}>
                        Sign out
                    </button>
                </div>
            </aside>

            {/* ── Main Content ── */}
            <main className="main-content">
                {children}
            </main>
        </div>
    )
}
