import { useState } from 'react'
import { recommendByNL } from '../api'
import SongCard from './SongCard'

const PLAYLISTS = [
  { name: 'Party Starter', emoji: '🎉', query: 'upbeat party music happy electronic pop high energy', desc: 'High-energy bangers', color: '#f59e0b' },
  { name: 'Deep Focus',    emoji: '🧠', query: 'calm study songs chill instrumental dreamy focus',    desc: 'Calm focus music',   color: '#6366f1' },
  { name: 'Pump Up',       emoji: '💪', query: 'intense workout tracks strong rock aggressive energy', desc: 'Workout intensity',  color: '#ef4444' },
  { name: 'Night Vibes',   emoji: '🌙', query: 'moody atmospheric night music emotional vocal dark',  desc: 'Late night mood',    color: '#8b5cf6' },
  { name: 'Morning',       emoji: '☀️', query: 'bright uplifting morning pop happy energetic day',    desc: 'Start your day',    color: '#f97316' },
  { name: 'Coffee Shop',   emoji: '☕', query: 'easy acoustic chill relaxed coffee lofi jazz',         desc: 'Relaxed vibes',     color: '#10b981' },
]

export default function PlaylistsTab({ sessionId, onSession }) {
  const [active, setActive] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(null)

  const play = async (pl) => {
    setActive(pl.name); setLoading(pl.name)
    try {
      const data = await recommendByNL({ query: pl.query, session_id: sessionId, k: 5 })
      setResults({ ...data, name: pl.name, emoji: pl.emoji })
      onSession(data.session_id)
    } finally { setLoading(null) }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
        <p style={{ fontWeight: 800, fontSize: 14, color: 'var(--text)' }}>🎧 Ready-Made Playlists</p>
        <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 20, background: 'rgba(139,92,246,0.15)', color: '#8b5cf6', fontWeight: 700, border: '1px solid rgba(139,92,246,0.25)' }}>Curated</span>
      </div>

      <div className="stagger" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 32 }}>
        {PLAYLISTS.map(pl => (
          <button key={pl.name} onClick={() => play(pl)}
            aria-pressed={active === pl.name}
            aria-busy={loading === pl.name}
            className="anim-fade-up"
            style={{
              textAlign: 'left', padding: '18px 18px 14px', borderRadius: 'var(--radius)', border: 'none', cursor: 'pointer',
              background: active === pl.name
                ? `linear-gradient(135deg, ${pl.color}18, ${pl.color}08)`
                : 'var(--card)',
              outline: active === pl.name ? `1px solid ${pl.color}55` : '1px solid var(--border)',
              transition: 'all 0.22s',
              position: 'relative', overflow: 'hidden',
            }}
            onMouseEnter={e => { if (active !== pl.name) { e.currentTarget.style.outline = '1px solid var(--border2)'; e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = `0 8px 24px ${pl.color}15` } }}
            onMouseLeave={e => { if (active !== pl.name) { e.currentTarget.style.outline = '1px solid var(--border)'; e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' } }}
          >
            {/* Gradient accent top */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: active === pl.name ? `linear-gradient(90deg, ${pl.color}, transparent)` : 'transparent', transition: 'all 0.3s' }} />

            <div style={{ fontSize: 26, marginBottom: 8 }}>{pl.emoji}</div>
            <p style={{ fontWeight: 700, color: active === pl.name ? pl.color : 'var(--text)', fontSize: 13, margin: '0 0 4px', transition: 'color 0.2s' }}>{pl.name}</p>
            <p style={{ color: 'var(--text3)', fontSize: 11, margin: '0 0 12px' }}>{pl.desc}</p>
            <span style={{
              fontSize: 11, padding: '3px 10px', borderRadius: 20, fontWeight: 600,
              background: `${pl.color}20`, color: pl.color,
              border: `1px solid ${pl.color}40`,
            }}>{loading === pl.name ? '⏳ Loading…' : active === pl.name ? '✓ Playing' : '▶ Play'}</span>
          </button>
        ))}
      </div>

      {results && (
        <div className="anim-fade-up">
          <p style={{ fontWeight: 800, fontSize: 14, color: 'var(--text)', marginBottom: 14 }}>{results.emoji} {results.name}</p>
          <div className="stagger">
            {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} style={{ marginBottom: 10 }} />)}
          </div>
        </div>
      )}
    </div>
  )
}
