'use client'

import { useEffect, useState } from 'react'
import { clipsApi, postingApi } from '@/lib/api'

const PLATFORMS = [
    { id: 'youtube_shorts', label: 'YouTube Shorts', icon: '▶️' },
    { id: 'tiktok', label: 'TikTok', icon: '🎵' },
    { id: 'instagram_reels', label: 'Instagram Reels', icon: '📸' },
    { id: 'facebook_reels', label: 'Facebook Reels', icon: '👍' },
]

export default function ClipsPage() {
    const [clips, setClips] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [publishingClip, setPublishingClip] = useState<string | null>(null)
    const [selectedPlatforms, setSelectedPlatforms] = useState<Record<string, string[]>>({})

    useEffect(() => {
        clipsApi.list({ limit: 50 }).then(r => setClips(r.data)).finally(() => setLoading(false))
    }, [])

    const togglePlatform = (clipId: string, platform: string) => {
        setSelectedPlatforms(prev => {
            const current = prev[clipId] || []
            return {
                ...prev,
                [clipId]: current.includes(platform)
                    ? current.filter(p => p !== platform)
                    : [...current, platform],
            }
        })
    }

    const publishClip = async (clipId: string) => {
        const platforms = selectedPlatforms[clipId] || []
        if (!platforms.length) return alert('Select at least one platform')
        setPublishingClip(clipId)
        try {
            await Promise.all(
                platforms.map(platform =>
                    postingApi.create({ clip_id: clipId, platform })
                )
            )
            alert(`✅ Queued to ${platforms.length} platform(s)!`)
        } catch (e: any) {
            alert(e.response?.data?.detail || 'Failed to queue post')
        } finally {
            setPublishingClip(null)
        }
    }

    const deleteClip = async (id: string) => {
        if (!confirm('Delete this clip?')) return
        await clipsApi.delete(id)
        setClips(prev => prev.filter(c => c.id !== id))
    }

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>My Clips</h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{clips.length} clips total</p>
                </div>
                <a href="/dashboard/generate">
                    <button className="btn-primary">+ Generate New</button>
                </a>
            </div>

            {loading ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
                    {[0, 1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton" style={{ height: '380px', borderRadius: '1rem' }} />)}
                </div>
            ) : clips.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎬</div>
                    <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>No clips yet</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Generate your first clip from a YouTube video</p>
                    <a href="/dashboard/generate"><button className="btn-primary">Generate Clips</button></a>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
                    {clips.map(clip => (
                        <div key={clip.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                            {/* Thumbnail */}
                            <div style={{
                                borderRadius: '0.75rem', overflow: 'hidden', aspectRatio: '9/5',
                                background: 'var(--bg-secondary)', marginBottom: '1rem', position: 'relative',
                            }}>
                                {clip.thumbnail_url ? (
                                    <img src={clip.thumbnail_url} alt={clip.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                ) : (
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', fontSize: '2.5rem' }}>🎬</div>
                                )}
                                {/* Viral score badge */}
                                {clip.viral_score > 0 && (
                                    <div style={{ position: 'absolute', top: 8, right: 8, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)', padding: '0.25rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700, color: '#10b981' }}>
                                        🔥 {clip.viral_score.toFixed(0)}
                                    </div>
                                )}
                                {/* Duration */}
                                {clip.duration && (
                                    <div style={{ position: 'absolute', bottom: 8, left: 8, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 600 }}>
                                        {Math.round(clip.duration)}s
                                    </div>
                                )}
                            </div>

                            {/* Title */}
                            <h3 style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.5rem', lineHeight: 1.4 }}>
                                {clip.title || 'Untitled clip'}
                            </h3>

                            {/* Tags */}
                            <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                                <span className={`badge ${clip.status === 'ready' ? 'badge-green' : clip.status === 'failed' ? 'badge-red' : 'badge-orange'}`} style={{ fontSize: '0.65rem' }}>
                                    {clip.status}
                                </span>
                                {clip.has_captions && <span className="badge badge-purple" style={{ fontSize: '0.65rem' }}>CC</span>}
                                {clip.is_vertical && <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>9:16</span>}
                                {clip.has_broll && <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>B-roll</span>}
                            </div>

                            {/* Platform selector */}
                            {clip.status === 'ready' && (
                                <div style={{ marginTop: 'auto' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 500 }}>Post to:</div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', marginBottom: '0.75rem' }}>
                                        {PLATFORMS.map(p => {
                                            const selected = (selectedPlatforms[clip.id] || []).includes(p.id)
                                            return (
                                                <button
                                                    key={p.id}
                                                    onClick={() => togglePlatform(clip.id, p.id)}
                                                    style={{
                                                        padding: '0.4rem 0.5rem', borderRadius: '0.5rem', border: selected ? '1px solid rgba(124,92,252,0.5)' : '1px solid var(--border)',
                                                        background: selected ? 'rgba(124,92,252,0.12)' : 'transparent', cursor: 'pointer',
                                                        color: 'var(--text-primary)', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.3rem',
                                                        transition: 'all 0.15s',
                                                    }}
                                                >
                                                    {p.icon} {p.label}
                                                </button>
                                            )
                                        })}
                                    </div>
                                    <button
                                        className="btn-primary"
                                        onClick={() => publishClip(clip.id)}
                                        disabled={publishingClip === clip.id || !(selectedPlatforms[clip.id]?.length)}
                                        style={{ width: '100%', justifyContent: 'center', padding: '0.6rem', fontSize: '0.85rem' }}
                                    >
                                        {publishingClip === clip.id ? '⏳ Queuing...' : '📤 Publish'}
                                    </button>
                                </div>
                            )}

                            {/* S3 link + delete */}
                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                                {clip.s3_url && (
                                    <a href={clip.s3_url} target="_blank" rel="noopener" style={{ flex: 1 }}>
                                        <button className="btn-secondary" style={{ width: '100%', padding: '0.4rem', fontSize: '0.8rem' }}>⬇️ Download</button>
                                    </a>
                                )}
                                <button className="btn-danger" onClick={() => deleteClip(clip.id)} style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>🗑️</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
