'use client'

import { useEffect, useState } from 'react'
import { channelsApi } from '@/lib/api'

export default function ChannelsPage() {
    const [channels, setChannels] = useState<any[]>([])
    const [videos, setVideos] = useState<Record<string, any[]>>({})
    const [loading, setLoading] = useState(true)
    const [oauthUrl, setOauthUrl] = useState('')

    useEffect(() => {
        channelsApi.list().then(r => setChannels(r.data)).finally(() => setLoading(false))
        // Build OAuth URL for YouTube
        const params = new URLSearchParams({
            client_id: process.env.NEXT_PUBLIC_YOUTUBE_CLIENT_ID || '',
            redirect_uri: `${window.location.origin}/api/auth/youtube/callback`,
            response_type: 'code',
            scope: 'https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload',
            access_type: 'offline',
            prompt: 'consent',
        })
        setOauthUrl(`https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`)
    }, [])

    const loadVideos = async (channelId: string) => {
        if (videos[channelId]) return
        const res = await channelsApi.videos(channelId)
        setVideos(prev => ({ ...prev, [channelId]: res.data.videos }))
    }

    const removeChannel = async (id: string) => {
        if (!confirm('Disconnect this channel?')) return
        await channelsApi.remove(id)
        setChannels(prev => prev.filter(c => c.id !== id))
    }

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Channels</h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Connect YouTube channels to auto-process new videos.</p>
                </div>
                <a href={oauthUrl} style={{ textDecoration: 'none' }}>
                    <button id="connect-youtube" className="btn-primary">
                        ▶️ Connect YouTube
                    </button>
                </a>
            </div>

            {/* Info box */}
            <div className="card" style={{ marginBottom: '1.5rem', background: 'rgba(59,130,246,0.05)', borderColor: 'rgba(59,130,246,0.2)' }}>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <span style={{ fontSize: '1.25rem' }}>ℹ️</span>
                    <div>
                        <div style={{ fontWeight: 600, marginBottom: '0.25rem', fontSize: '0.9rem' }}>How channel monitoring works</div>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                            Once connected, AutoUploader checks your channel every 30 minutes for new videos.
                            New videos are automatically queued for AI clip generation. You stay in control —
                            clips wait in "My Clips" until you approve and schedule posting.
                        </p>
                    </div>
                </div>
            </div>

            {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {[0, 1].map(i => <div key={i} className="skeleton" style={{ height: '100px', borderRadius: '1rem' }} />)}
                </div>
            ) : channels.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📺</div>
                    <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>No channels connected</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Connect your YouTube channel to start automatically generating clips from new uploads.</p>
                    <a href={oauthUrl}>
                        <button className="btn-primary">Connect YouTube Channel</button>
                    </a>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {channels.map(channel => (
                        <div key={channel.id} className="card">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                {channel.thumbnail_url ? (
                                    <img src={channel.thumbnail_url} alt={channel.channel_name} style={{ width: 52, height: 52, borderRadius: '50%', objectFit: 'cover' }} />
                                ) : (
                                    <div style={{ width: 52, height: 52, borderRadius: '50%', background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>📺</div>
                                )}
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 700, marginBottom: '0.25rem' }}>{channel.channel_name}</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{channel.platform} • Connected {new Date(channel.created_at).toLocaleDateString()}</div>
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button className="btn-secondary" onClick={() => loadVideos(channel.id)} style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                                        View Videos
                                    </button>
                                    <button className="btn-danger" onClick={() => removeChannel(channel.id)}>Disconnect</button>
                                </div>
                            </div>

                            {/* Videos list */}
                            {videos[channel.id] && (
                                <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--border)', paddingTop: '1.25rem' }}>
                                    <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>Recent Videos</div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {videos[channel.id].slice(0, 5).map((v: any) => (
                                            <div key={v.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.02)' }}>
                                                {v.thumbnail && (
                                                    <img src={v.thumbnail} alt={v.title} style={{ width: 60, height: 36, borderRadius: '4px', objectFit: 'cover', flexShrink: 0 }} />
                                                )}
                                                <div style={{ flex: 1, minWidth: 0 }}>
                                                    <div style={{ fontWeight: 500, fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v.title}</div>
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                                        {new Date(v.published_at || '').toLocaleDateString()}
                                                    </div>
                                                </div>
                                                <a href={`/dashboard/generate?url=https://youtube.com/watch?v=${v.id}`} style={{ flexShrink: 0 }}>
                                                    <button className="btn-primary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}>✂️ Clip</button>
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
