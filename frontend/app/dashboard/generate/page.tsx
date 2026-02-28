'use client'

import { useState } from 'react'
import { clipsApi } from '@/lib/api'

export default function GeneratePage() {
    const [youtubeUrl, setYoutubeUrl] = useState('')
    const [numClips, setNumClips] = useState(5)
    const [addCaptions, setAddCaptions] = useState(true)
    const [verticalFormat, setVerticalFormat] = useState(true)
    const [addBroll, setAddBroll] = useState(false)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState('')

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!youtubeUrl.trim()) return
        setLoading(true)
        setError('')
        setResult(null)
        try {
            const res = await clipsApi.generateFromUrl(youtubeUrl, numClips, addCaptions, verticalFormat)
            setResult(res.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to start clip generation.')
        } finally {
            setLoading(false)
        }
    }

    const STEPS = [
        { icon: '⬇️', label: 'Download', desc: 'yt-dlp fetches the video at max quality' },
        { icon: '🎤', label: 'Transcribe', desc: 'Whisper converts speech to text with timestamps' },
        { icon: '🤖', label: 'AI Selects', desc: 'GPT-4 scores and picks the viral moments' },
        { icon: '✂️', label: 'FFmpeg Cut', desc: 'Clips are cut precisely at the AI timestamps' },
        { icon: '📝', label: 'Captions', desc: 'Animated ASS captions burned in' },
        { icon: '📱', label: 'Vertical', desc: 'Smart blur-pad conversion to 9:16' },
        { icon: '☁️', label: 'Upload', desc: 'Clips uploaded to S3 storage' },
    ]

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Generate Clips</h1>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Paste a YouTube URL and let the AI do the work.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem', alignItems: 'start' }}>

                {/* Left: Form */}
                <div>
                    <div className="card" style={{ marginBottom: '1.5rem' }}>
                        <h2 style={{ fontWeight: 700, marginBottom: '1.5rem', fontSize: '1.1rem' }}>Video Source</h2>
                        <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                                    YouTube URL *
                                </label>
                                <input
                                    id="youtube-url"
                                    className="input"
                                    value={youtubeUrl}
                                    onChange={e => setYoutubeUrl(e.target.value)}
                                    placeholder="https://www.youtube.com/watch?v=..."
                                    required
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
                                    Number of Clips: <strong style={{ color: 'var(--text-primary)' }}>{numClips}</strong>
                                </label>
                                <input
                                    type="range" min={1} max={10} value={numClips}
                                    onChange={e => setNumClips(Number(e.target.value))}
                                    style={{ width: '100%', accentColor: 'var(--accent-purple)' }}
                                />
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                    <span>1</span><span>10</span>
                                </div>
                            </div>

                            {/* Toggles */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {[
                                    { id: 'toggle-captions', label: '📝 Animated Captions', desc: 'Burn styled captions via Whisper', value: addCaptions, setter: setAddCaptions },
                                    { id: 'toggle-vertical', label: '📱 Vertical Format (9:16)', desc: 'Convert to TikTok/Reels/Shorts format', value: verticalFormat, setter: setVerticalFormat },
                                    { id: 'toggle-broll', label: '🎬 AI B-Roll Insertion', desc: 'Add Pexels stock footage from keywords', value: addBroll, setter: setAddBroll },
                                ].map(toggle => (
                                    <div key={toggle.id} onClick={() => toggle.setter(!toggle.value)} style={{
                                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                        padding: '0.875rem 1rem', borderRadius: '0.75rem',
                                        border: toggle.value ? '1px solid rgba(124,92,252,0.4)' : '1px solid var(--border)',
                                        background: toggle.value ? 'rgba(124,92,252,0.08)' : 'transparent',
                                        cursor: 'pointer', transition: 'all 0.2s',
                                    }}>
                                        <div>
                                            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{toggle.label}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.1rem' }}>{toggle.desc}</div>
                                        </div>
                                        <div style={{
                                            width: 40, height: 22, borderRadius: '11px', position: 'relative',
                                            background: toggle.value ? 'var(--accent-purple)' : 'var(--border)',
                                            transition: 'background 0.2s', flexShrink: 0,
                                        }}>
                                            <div style={{
                                                position: 'absolute', top: 3, width: 16, height: 16, borderRadius: '50%',
                                                background: 'white', transition: 'left 0.2s',
                                                left: toggle.value ? 21 : 3,
                                            }} />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {error && (
                                <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '0.75rem', padding: '0.75rem 1rem', color: '#f87171', fontSize: '0.875rem' }}>
                                    {error}
                                </div>
                            )}

                            <button id="generate-btn" className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center', padding: '1rem' }}>
                                {loading ? (
                                    <><span className="spinner" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', marginRight: '0.5rem' }} />Processing...</>
                                ) : '🚀 Generate Clips with AI'}
                            </button>
                        </form>
                    </div>

                    {/* Result */}
                    {result && (
                        <div className="card" style={{ borderColor: 'rgba(16,185,129,0.4)', background: 'rgba(16,185,129,0.05)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                                <span style={{ fontSize: '1.5rem' }}>✅</span>
                                <div>
                                    <div style={{ fontWeight: 700 }}>Processing started!</div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Task ID: {result.task_id}</div>
                                </div>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '0.5rem', padding: '0.75rem' }}>
                                    <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Video</div>
                                    <div style={{ fontWeight: 600 }}>{result.video_title || 'YouTube video'}</div>
                                </div>
                                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '0.5rem', padding: '0.75rem' }}>
                                    <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Est. time</div>
                                    <div style={{ fontWeight: 600 }}>~{result.estimated_time_minutes || numClips * 3} min</div>
                                </div>
                            </div>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>
                                Clips will appear in <a href="/dashboard/clips" style={{ color: 'var(--accent-purple)' }}>My Clips</a> when ready.
                            </p>
                        </div>
                    )}
                </div>

                {/* Right: Pipeline visualization */}
                <div className="card" style={{ position: 'sticky', top: '2rem' }}>
                    <h3 style={{ fontWeight: 700, marginBottom: '1.25rem', fontSize: '1rem' }}>🤖 AI Pipeline</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                        {STEPS.map((step, i) => (
                            <div key={i} style={{ display: 'flex', gap: '0.75rem', position: 'relative' }}>
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                    <div style={{
                                        width: 36, height: 36, borderRadius: '50%',
                                        background: loading && i === 0 ? 'var(--gradient-1)' : 'var(--bg-card)',
                                        border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '1rem', flexShrink: 0, zIndex: 1,
                                        boxShadow: loading ? '0 0 15px rgba(124,92,252,0.3)' : 'none',
                                    }}>
                                        {step.icon}
                                    </div>
                                    {i < STEPS.length - 1 && (
                                        <div style={{ width: 1, height: 32, background: 'var(--border)', flexShrink: 0 }} />
                                    )}
                                </div>
                                <div style={{ paddingBottom: i < STEPS.length - 1 ? '0.5rem' : 0 }}>
                                    <div style={{ fontWeight: 600, fontSize: '0.85rem', lineHeight: '36px' }}>{step.label}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '-0.25rem', lineHeight: 1.5 }}>{step.desc}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
