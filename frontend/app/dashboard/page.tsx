'use client'

import { useEffect, useState } from 'react'
import { analyticsApi, clipsApi, usersApi } from '@/lib/api'
import Link from 'next/link'

export default function DashboardPage() {
    const [summary, setSummary] = useState<any>(null)
    const [clips, setClips] = useState<any[]>([])
    const [usage, setUsage] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            analyticsApi.summary(30),
            clipsApi.list({ limit: 5 }),
            usersApi.usage(),
        ]).then(([s, c, u]) => {
            setSummary(s.data)
            setClips(c.data)
            setUsage(u.data)
        }).finally(() => setLoading(false))
    }, [])

    const statCards = summary ? [
        { label: 'Total Views', value: (summary.total_views || 0).toLocaleString(), icon: '👁️', color: 'var(--accent-purple)', delta: '+12%' },
        { label: 'Total Likes', value: (summary.total_likes || 0).toLocaleString(), icon: '❤️', color: 'var(--accent-pink)', delta: '+8%' },
        { label: 'Clips Ready', value: summary.total_clips || 0, icon: '🎬', color: 'var(--accent-blue)', delta: null },
        { label: 'Posts Published', value: summary.total_posts || 0, icon: '📤', color: 'var(--accent-green)', delta: null },
    ] : []

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Dashboard</h1>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Welcome back! Here's your performance overview.</p>
            </div>

            {/* ── Usage bar ── */}
            {usage && (
                <div className="card" style={{ marginBottom: '2rem', display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Monthly clips</span>
                            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{usage.clips_generated} / {usage.max_clips}</span>
                        </div>
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${Math.min(100, (usage.clips_generated / usage.max_clips) * 100)}%` }} />
                        </div>
                    </div>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Channels</span>
                            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{usage.channels_connected} / {usage.max_channels}</span>
                        </div>
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${Math.min(100, (usage.channels_connected / usage.max_channels) * 100)}%`, background: 'var(--gradient-2)' }} />
                        </div>
                    </div>
                    <Link href="/dashboard/generate">
                        <button className="btn-primary">+ Generate Clips</button>
                    </Link>
                </div>
            )}

            {/* ── Stat cards ── */}
            {loading ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    {[0, 1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: '100px' }} />)}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    {statCards.map((s, i) => (
                        <div key={i} className="stat-card">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                <span style={{ fontSize: '1.5rem' }}>{s.icon}</span>
                                {s.delta && <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>{s.delta}</span>}
                            </div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{s.value}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{s.label}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* ── Platform breakdown ── */}
            {summary?.platform_breakdown && Object.keys(summary.platform_breakdown).length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Platform Breakdown</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                        {Object.entries(summary.platform_breakdown).map(([platform, data]: [string, any]) => {
                            const icons: Record<string, string> = { youtube_shorts: '▶️', tiktok: '🎵', instagram_reels: '📸', facebook_reels: '👍' }
                            const colors: Record<string, string> = { youtube_shorts: 'badge-red', tiktok: 'badge-cyan', instagram_reels: 'badge-purple', facebook_reels: 'badge-blue' }
                            return (
                                <div key={platform} className="card" style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{icons[platform] || '📱'}</div>
                                    <div className={`badge ${colors[platform] || 'badge-purple'}`} style={{ marginBottom: '0.75rem', fontSize: '0.7rem' }}>{platform.replace('_', ' ')}</div>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{(data.views || 0).toLocaleString()}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>views</div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* ── Recent clips ── */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Recent Clips</h2>
                    <Link href="/dashboard/clips" style={{ color: 'var(--accent-purple)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 500 }}>View all →</Link>
                </div>
                {loading ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {[0, 1, 2].map(i => <div key={i} className="skeleton" style={{ height: '60px' }} />)}
                    </div>
                ) : clips.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✂️</div>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>No clips yet. Generate your first clip!</p>
                        <Link href="/dashboard/generate"><button className="btn-primary">Generate Clips</button></Link>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Duration</th>
                                    <th>Viral Score</th>
                                    <th>Status</th>
                                    <th>Features</th>
                                </tr>
                            </thead>
                            <tbody>
                                {clips.map((clip) => (
                                    <tr key={clip.id}>
                                        <td style={{ fontWeight: 500 }}>{clip.title || 'Untitled clip'}</td>
                                        <td style={{ color: 'var(--text-secondary)' }}>{clip.duration ? `${Math.round(clip.duration)}s` : '—'}</td>
                                        <td>
                                            {clip.viral_score ? (
                                                <span style={{ color: clip.viral_score >= 80 ? '#10b981' : clip.viral_score >= 60 ? '#f59e0b' : '#ef4444', fontWeight: 600 }}>
                                                    🔥 {clip.viral_score.toFixed(0)}
                                                </span>
                                            ) : '—'}
                                        </td>
                                        <td>
                                            <span className={`badge ${clip.status === 'ready' ? 'badge-green' : clip.status === 'processing' ? 'badge-blue' : clip.status === 'failed' ? 'badge-red' : 'badge-orange'}`}>
                                                {clip.status}
                                            </span>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                                                {clip.has_captions && <span className="badge badge-purple" style={{ fontSize: '0.65rem' }}>CC</span>}
                                                {clip.is_vertical && <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>9:16</span>}
                                                {clip.has_broll && <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>B-roll</span>}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
