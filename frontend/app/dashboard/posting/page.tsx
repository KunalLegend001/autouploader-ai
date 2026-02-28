'use client'

import { useEffect, useState } from 'react'
import { postingApi } from '@/lib/api'

const PLATFORM_ICONS: Record<string, string> = {
    youtube_shorts: '▶️', tiktok: '🎵', instagram_reels: '📸', facebook_reels: '👍',
}
const STATUS_BADGE: Record<string, string> = {
    pending: 'badge-orange', queued: 'badge-blue', uploading: 'badge-purple',
    published: 'badge-green', failed: 'badge-red',
}

export default function PostingPage() {
    const [posts, setPosts] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        postingApi.list().then(r => setPosts(r.data)).finally(() => setLoading(false))
    }, [])

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Auto-Post Queue</h1>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>All scheduled and published posts across platforms.</p>
            </div>

            {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {[0, 1, 2, 3, 4].map(i => <div key={i} className="skeleton" style={{ height: '70px', borderRadius: '0.75rem' }} />)}
                </div>
            ) : posts.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📤</div>
                    <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>No posts yet</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Head to My Clips and publish your first clip to a platform.</p>
                    <a href="/dashboard/clips"><button className="btn-primary">Go to My Clips</button></a>
                </div>
            ) : (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Platform</th>
                                <th>Title</th>
                                <th>Status</th>
                                <th>Scheduled</th>
                                <th>Published</th>
                                <th>Link</th>
                            </tr>
                        </thead>
                        <tbody>
                            {posts.map(post => (
                                <tr key={post.id}>
                                    <td>
                                        <span style={{ fontSize: '1.2rem', marginRight: '0.5rem' }}>{PLATFORM_ICONS[post.platform] || '📱'}</span>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{post.platform?.replace('_', ' ')}</span>
                                    </td>
                                    <td style={{ fontWeight: 500, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {post.title || 'Untitled'}
                                    </td>
                                    <td>
                                        <span className={`badge ${STATUS_BADGE[post.status] || 'badge-orange'}`} style={{ fontSize: '0.7rem' }}>
                                            {post.status}
                                        </span>
                                    </td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        {post.scheduled_at ? new Date(post.scheduled_at).toLocaleString() : 'Immediate'}
                                    </td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        {post.published_at ? new Date(post.published_at).toLocaleString() : '—'}
                                    </td>
                                    <td>
                                        {post.post_url ? (
                                            <a href={post.post_url} target="_blank" rel="noopener" style={{ color: 'var(--accent-purple)', fontWeight: 500, fontSize: '0.85rem', textDecoration: 'none' }}>
                                                View ↗
                                            </a>
                                        ) : '—'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
