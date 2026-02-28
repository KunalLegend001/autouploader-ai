'use client'

import { useEffect, useState } from 'react'
import { analyticsApi } from '@/lib/api'

const PLATFORM_ICONS: Record<string, string> = {
    youtube_shorts: '▶️', tiktok: '🎵', instagram_reels: '📸', facebook_reels: '👍',
}
const PLATFORM_COLORS: Record<string, string> = {
    youtube_shorts: '#ff0000', tiktok: '#69c9d0', instagram_reels: '#e1306c', facebook_reels: '#1877f2',
}

export default function AnalyticsPage() {
    const [summary, setSummary] = useState<any>(null)
    const [days, setDays] = useState(30)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setLoading(true)
        analyticsApi.summary(days).then(r => setSummary(r.data)).finally(() => setLoading(false))
    }, [days])

    const statCards = summary ? [
        { label: 'Total Views', value: (summary.total_views || 0).toLocaleString(), icon: '👁️', detail: 'Across all platforms' },
        { label: 'Total Likes', value: (summary.total_likes || 0).toLocaleString(), icon: '❤️', detail: 'Engagement signals' },
        { label: 'Total Comments', value: (summary.total_comments || 0).toLocaleString(), icon: '💬', detail: 'Community interaction' },
        { label: 'Total Shares', value: (summary.total_shares || 0).toLocaleString(), icon: '🔁', detail: 'Virality metric' },
        { label: 'Avg Engagement', value: `${((summary.avg_engagement_rate || 0) * 100).toFixed(1)}%`, icon: '📈', detail: 'Average across posts' },
        { label: 'Posts Published', value: summary.total_posts || 0, icon: '📤', detail: 'Total postings' },
    ] : []

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Analytics</h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Performance across all platforms</p>
                </div>
                {/* Period selector */}
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {[7, 30, 90].map(d => (
                        <button key={d} onClick={() => setDays(d)} style={{
                            padding: '0.5rem 1rem', borderRadius: '0.75rem', border: days === d ? '1px solid rgba(124,92,252,0.5)' : '1px solid var(--border)',
                            background: days === d ? 'rgba(124,92,252,0.15)' : 'transparent', color: days === d ? 'white' : 'var(--text-secondary)',
                            cursor: 'pointer', fontSize: '0.85rem', fontWeight: days === d ? 600 : 400, transition: 'all 0.2s',
                        }}>
                            {d}d
                        </button>
                    ))}
                </div>
            </div>

            {/* Stat grid */}
            {loading ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    {[0, 1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton" style={{ height: '110px', borderRadius: '1rem' }} />)}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    {statCards.map((s, i) => (
                        <div key={i} className="stat-card">
                            <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{s.icon}</div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{s.value}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.85rem', marginTop: '0.25rem' }}>{s.label}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{s.detail}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* Platform breakdown */}
            {summary?.platform_breakdown && Object.keys(summary.platform_breakdown).length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Platform Breakdown</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                        {Object.entries(summary.platform_breakdown).map(([platform, data]: [string, any]) => {
                            const totalViews = summary.total_views || 1
                            const pct = Math.round(((data.views || 0) / totalViews) * 100)
                            return (
                                <div key={platform} className="card">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                                        <span style={{ fontSize: '1.5rem' }}>{PLATFORM_ICONS[platform] || '📱'}</span>
                                        <div>
                                            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{platform.replace('_', ' ')}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{data.posts || 0} posts</div>
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem' }}>
                                        <div>
                                            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{(data.views || 0).toLocaleString()}</div>
                                            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>views</div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{(data.likes || 0).toLocaleString()}</div>
                                            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>likes</div>
                                        </div>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${pct}%`, background: PLATFORM_COLORS[platform] || 'var(--accent-purple)' }} />
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{pct}% of total views</div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Best performing clip */}
            {summary?.best_performing_clip && (
                <div>
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>🏆 Best Performing Clip</h2>
                    <div className="card" style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', borderColor: 'rgba(245,158,11,0.3)', background: 'rgba(245,158,11,0.04)' }}>
                        <div style={{
                            width: 80, height: 80, borderRadius: '0.75rem', background: 'var(--bg-secondary)',
                            flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.75rem',
                        }}>
                            {summary.best_performing_clip.thumbnail_url ? (
                                <img src={summary.best_performing_clip.thumbnail_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '0.75rem' }} />
                            ) : '🎬'}
                        </div>
                        <div style={{ flex: 1 }}>
                            <h3 style={{ fontWeight: 700, marginBottom: '0.25rem' }}>{summary.best_performing_clip.title || 'Untitled'}</h3>
                            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                                {summary.best_performing_clip.viral_score && (
                                    <span style={{ color: '#10b981', fontWeight: 600, fontSize: '0.9rem' }}>🔥 Score: {summary.best_performing_clip.viral_score}</span>
                                )}
                                {summary.best_performing_clip.duration && (
                                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{Math.round(summary.best_performing_clip.duration)}s</span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty state */}
            {!loading && !summary?.total_posts && (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📊</div>
                    <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>No analytics yet</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>Post some clips and analytics will appear here.</p>
                </div>
            )}
        </div>
    )
}
