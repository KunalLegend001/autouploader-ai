'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function HomePage() {
  const [videoUrl, setVideoUrl] = useState('')

  return (
    <main style={{ minHeight: '100vh', background: 'var(--bg-primary)', overflow: 'hidden' }}>

      {/* ── Nav ─────────────────────────────────────── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        background: 'rgba(8,11,20,0.8)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border)', padding: '0 2rem', height: '64px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 36, height: 36, borderRadius: '10px',
            background: 'var(--gradient-1)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.1rem',
          }}>🚀</div>
          <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>AutoUploader</span>
          <span className="badge badge-purple" style={{ marginLeft: '0.25rem' }}>AI</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '0.9rem' }}>Features</a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '0.9rem' }}>Pricing</a>
          <Link href="/login">
            <button className="btn-secondary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>Sign in</button>
          </Link>
          <Link href="/register">
            <button className="btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>Start free</button>
          </Link>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────── */}
      <section style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', textAlign: 'center', padding: '8rem 2rem 4rem',
        background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(124,92,252,0.15) 0%, transparent 70%)',
      }}>
        <div className="animate-fade-in">
          <div className="badge badge-purple" style={{ marginBottom: '1.5rem', fontSize: '0.8rem', padding: '0.4rem 1rem' }}>
            ✨ Powered by GPT-4 + Whisper AI
          </div>
          <h1 style={{ fontSize: 'clamp(2.5rem, 6vw, 5rem)', fontWeight: 900, lineHeight: 1.1, marginBottom: '1.5rem', letterSpacing: '-0.03em' }}>
            Turn Long Videos Into<br />
            <span className="gradient-text">Viral Short Clips</span>
            <br />Automatically
          </h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 2.5rem', lineHeight: 1.7 }}>
            AI finds your best moments, adds captions & B-roll, converts to vertical format,
            and posts to TikTok, Reels, and YouTube Shorts — fully on autopilot.
          </p>

          {/* CTA URL input */}
          <div style={{
            display: 'flex', gap: '0.75rem', maxWidth: '600px', margin: '0 auto 3rem',
            background: 'var(--bg-card)', border: '1px solid var(--border-glow)',
            borderRadius: '1rem', padding: '0.5rem',
          }}>
            <input
              className="input"
              value={videoUrl}
              onChange={e => setVideoUrl(e.target.value)}
              placeholder="Paste a YouTube URL..."
              style={{ border: 'none', background: 'transparent', flex: 1 }}
            />
            <Link href="/register">
              <button className="btn-primary" style={{ whiteSpace: 'nowrap' }}>
                🎬 Generate Clips
              </button>
            </Link>
          </div>

          {/* Social proof */}
          <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {[
              { value: '2M+', label: 'Clips Generated' },
              { value: '50K+', label: 'Creators' },
              { value: '4.9★', label: 'Rating' },
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, background: 'var(--gradient-1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Demo visual */}
        <div style={{ marginTop: '5rem', position: 'relative', maxWidth: '900px', width: '100%' }}>
          <div className="glass" style={{ borderRadius: '1.5rem', padding: '1.5rem', border: '1px solid var(--border-glow)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {[
                { title: 'The secret to building wealth', score: 94, tag: 'Finance', platform: '🎵 TikTok' },
                { title: 'Why most people never succeed', score: 87, tag: 'Motivation', platform: '📸 Reels' },
                { title: 'This changed everything for me', score: 91, tag: 'Personal', platform: '▶️ Shorts' },
              ].map((clip, i) => (
                <div key={i} className="card" style={{ padding: '1rem', textAlign: 'left' }}>
                  <div style={{ background: 'var(--gradient-hero)', borderRadius: '0.75rem', height: '120px', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem' }}>
                    🎬
                  </div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>{clip.title}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                    <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>{clip.tag}</span>
                    <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600 }}>🔥 {clip.score}</span>
                  </div>
                  <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{clip.platform}</div>
                </div>
              ))}
            </div>
          </div>
          {/* Glow behind */}
          <div style={{ position: 'absolute', bottom: '-60px', left: '50%', transform: 'translateX(-50%)', width: '60%', height: '60px', background: 'rgba(124,92,252,0.3)', filter: 'blur(40px)', borderRadius: '50%' }} />
        </div>
      </section>

      {/* ── Features ─────────────────────────────────── */}
      <section id="features" style={{ padding: '6rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 800, textAlign: 'center', marginBottom: '0.75rem' }}>
          Everything you need to <span className="gradient-text">go viral</span>
        </h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '4rem', fontSize: '1.1rem' }}>
          One platform. Six powerful AI modules. Zero manual work.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {[
            { icon: '🎯', title: 'AI Clip Detection', desc: 'GPT-4 analyzes your transcript and scores moments by viral potential, automatically finding gold.', color: 'var(--accent-purple)' },
            { icon: '📝', title: 'Animated Captions', desc: 'Whisper transcribes with word-level timestamps. FFmpeg burns modern animated captions.', color: 'var(--accent-blue)' },
            { icon: '📱', title: 'Smart Vertical Format', desc: 'Blur-pad technique converts any video to 9:16 while keeping the speaker in frame.', color: 'var(--accent-cyan)' },
            { icon: '🎬', title: 'AI B-Roll', desc: 'Keywords extracted from transcript trigger automatic Pexels stock footage insertion.', color: 'var(--accent-pink)' },
            { icon: '📤', title: 'Auto-Posting', desc: 'One click schedules posts to TikTok, Instagram Reels, YouTube Shorts, and Facebook.', color: 'var(--accent-green)' },
            { icon: '📊', title: 'Analytics Dashboard', desc: 'Real-time performance tracking across all platforms. See what\'s going viral.', color: 'var(--accent-orange)' },
          ].map((f, i) => (
            <div key={i} className="card glass-hover" style={{ animationDelay: `${i * 0.1}s` }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{f.icon}</div>
              <h3 style={{ fontWeight: 700, marginBottom: '0.5rem', fontSize: '1.1rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.7 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pricing ──────────────────────────────────── */}
      <section id="pricing" style={{ padding: '6rem 2rem', background: 'radial-gradient(ellipse 60% 30% at 50% 100%, rgba(124,92,252,0.08), transparent)' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 800, textAlign: 'center', marginBottom: '0.75rem' }}>Simple pricing</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '4rem' }}>Start free, scale as you grow</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem' }}>
            {[
              { name: 'Free', price: '$0', features: ['30 clips/month', '3 channels', 'Auto captions', 'Vertical format', '1 platform'], cta: 'Get started', highlight: false },
              { name: 'Pro', price: '$29', features: ['300 clips/month', '10 channels', 'AI B-roll', 'All platforms', 'Priority processing', 'Analytics API'], cta: 'Start Pro', highlight: true },
              { name: 'Agency', price: '$99', features: ['Unlimited clips', 'Unlimited channels', 'White label', 'Team access', 'Dedicated support', 'Custom branding'], cta: 'Contact us', highlight: false },
            ].map((plan, i) => (
              <div key={i} className={plan.highlight ? 'animate-pulse-glow' : ''} style={{
                background: plan.highlight ? 'linear-gradient(135deg, rgba(124,92,252,0.15), rgba(59,130,246,0.1))' : 'var(--bg-card)',
                border: plan.highlight ? '1px solid rgba(124,92,252,0.5)' : '1px solid var(--border)',
                borderRadius: '1.25rem', padding: '2rem', textAlign: 'center',
              }}>
                {plan.highlight && <div className="badge badge-purple" style={{ marginBottom: '1rem' }}>Most Popular</div>}
                <h3 style={{ fontWeight: 700, fontSize: '1.25rem', marginBottom: '0.5rem' }}>{plan.name}</h3>
                <div style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '1.5rem' }}>
                  {plan.price}<span style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 400 }}>/mo</span>
                </div>
                <ul style={{ listStyle: 'none', marginBottom: '2rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {plan.features.map(f => (
                    <li key={f} style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#10b981' }}>✓</span> {f}
                    </li>
                  ))}
                </ul>
                <Link href="/register">
                  <button className={plan.highlight ? 'btn-primary' : 'btn-secondary'} style={{ width: '100%' }}>
                    {plan.cta}
                  </button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <p>© 2026 AutoUploader AI. Built with ❤️ and GPT-4.</p>
      </footer>
    </main>
  )
}
