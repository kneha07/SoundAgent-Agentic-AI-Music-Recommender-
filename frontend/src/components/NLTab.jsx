import { useState } from 'react'
import { recommendByNL } from '../api'
import SongCard from './SongCard'

const SAMPLES = [
  { text: 'Upbeat party music for a happy listener who loves electronic pop', icon: '🎉' },
  { text: 'Calm study songs with a chill mood and dreamy textures', icon: '📚' },
  { text: 'Intense workout tracks with strong rock energy', icon: '💪' },
  { text: 'Sad but powerful night music that is emotional and vocal-heavy', icon: '🌙' },
]

export default function NLTab({ sessionId, onSession }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const submit = async (q) => {
    const text = (q || query).trim()
    if (!text) return
    setQuery(text); setLoading(true); setError(null)
    try {
      const data = await recommendByNL({ query: text, session_id: sessionId, k: 5 })
      setResults(data); onSession(data.session_id)
    } catch { setError('Could not reach the API — is it running?') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28, alignItems: 'start' }}>

      {/* Left */}
      <div className="anim-fade-up">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
          <p style={{ fontWeight: 800, fontSize: 14, color: 'var(--text)' }}>💬 Natural Language Request</p>
          <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 20, background: 'rgba(6,182,212,0.15)', color: 'var(--cyan)', fontWeight: 700, border: '1px solid rgba(6,182,212,0.25)' }}>AI-Powered</span>
        </div>

        <p style={{ fontSize: 12, color: 'var(--text3)', marginBottom: 10, fontWeight: 600 }}>Try a sample:</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7, marginBottom: 20 }}>
          {SAMPLES.map(s => (
            <button key={s.text} onClick={() => submit(s.text)}
              aria-label={`Try: ${s.text}`}
              style={{
                textAlign: 'left', padding: '10px 12px', borderRadius: 'var(--radius-sm)',
                background: 'var(--card)', border: '1px solid var(--border)',
                color: 'var(--text2)', cursor: 'pointer', fontSize: 12, lineHeight: 1.4,
                transition: 'all 0.2s', display: 'flex', gap: 7, alignItems: 'flex-start',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.background = 'var(--card2)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--card)' }}
            >
              <span style={{ flexShrink: 0 }}>{s.icon}</span>
              <span style={{ overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{s.text}</span>
            </button>
          ))}
        </div>

        <label htmlFor="nl-input" style={{ display: 'block', fontSize: 12, color: 'var(--text2)', fontWeight: 600, marginBottom: 6 }}>Describe your ideal playlist</label>
        <textarea id="nl-input" value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), submit())}
          placeholder="e.g. chill lo-fi beats for a rainy afternoon with coffee…" rows={4}
          className="input" style={{ resize: 'none' }} />

        <button onClick={() => submit()} disabled={loading || !query.trim()} className="btn" style={{ marginTop: 10 }} aria-busy={loading}>
          {loading
            ? <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}><span className="anim-spin">◌</span> Finding…</span>
            : '🔍 Find My Songs'}
        </button>
        {error && <p role="alert" style={{ color: '#f87171', fontSize: 12, marginTop: 8 }}>{error}</p>}
      </div>

      {/* Right */}
      <section aria-label="Natural language results" className="anim-fade-up" style={{ animationDelay: '0.1s' }}>
        {results ? (
          <div>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <p style={{ fontWeight: 800, fontSize: 14, color: 'var(--text)' }}>🎶 Your Playlist</p>
              {results.confidence && <Badge color="var(--green)">{Math.round(results.confidence * 100)}% confidence</Badge>}
              {results.mode && <Badge color="var(--cyan)">{results.mode}</Badge>}
            </div>
            {results.explanation && (
              <div className="card" style={{ padding: '12px 14px', marginBottom: 14, fontSize: 13, color: 'var(--text2)', fontStyle: 'italic', borderLeft: '3px solid var(--cyan)' }}>
                {results.explanation}
              </div>
            )}
            <div className="stagger">
              {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} style={{ marginBottom: 10 }} />)}
            </div>
          </div>
        ) : (
          <div className="card" style={{ padding: 48, textAlign: 'center', color: 'var(--text3)', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, minHeight: 200 }}>
            <div style={{ fontSize: 40 }}>💬</div>
            <p style={{ fontWeight: 600, color: 'var(--text2)', fontSize: 14 }}>Describe your vibe</p>
            <p style={{ fontSize: 12 }}>Type anything and the AI will find the perfect songs.</p>
          </div>
        )}
      </section>
    </div>
  )
}

function Badge({ color, children }) {
  return <span style={{ fontSize: 11, padding: '3px 9px', borderRadius: 20, background: `${color}18`, color, border: `1px solid ${color}44`, fontWeight: 600 }}>{children}</span>
}
