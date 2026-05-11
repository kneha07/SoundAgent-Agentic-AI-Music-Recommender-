import { useState } from 'react'
import { recommendByProfile } from '../api'
import SongCard from './SongCard'

const MOODS    = ['happy','sad','chill','intense','focused','moody','relaxed']
const GENRES   = ['pop','rock','jazz','lofi','house','synthwave','indie','ambient','r&b','folk']
const CONTEXTS = ['general','study','workout','party','relax','night','drive','coffee']

const MOOD_COLORS = { happy:'#fbbf24', sad:'#60a5fa', chill:'#34d399', intense:'#f87171', focused:'#a78bfa', moody:'#f472b6', relaxed:'#6ee7b7' }

export default function ProfileTab({ sessionId, onSession }) {
  const [form, setForm] = useState({ mood:'happy', energy:0.7, genre:'pop', vocal:'vocal', context:'general', k:5 })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async () => {
    setLoading(true); setError(null)
    try {
      const data = await recommendByProfile({ ...form, session_id: sessionId })
      setResults(data); onSession(data.session_id)
    } catch { setError('Could not reach the API — is it running?') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 28, alignItems: 'start' }}>

      {/* ── Form panel ── */}
      <aside className="card anim-fade-up" style={{ padding: '20px', position: 'sticky', top: 72 }}>
        <p style={{ fontWeight: 800, fontSize: 14, color: 'var(--text)', marginBottom: 18, display: 'flex', alignItems: 'center', gap: 7 }}>
          <span>⚙️</span> Your Preferences
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Mood with color dots */}
          <Field label="Mood">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
              {MOODS.map(m => (
                <button key={m} onClick={() => set('mood', m)}
                  aria-pressed={form.mood === m}
                  style={{
                    padding: '4px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600, border: 'none', cursor: 'pointer',
                    background: form.mood === m ? `${MOOD_COLORS[m]}22` : 'rgba(255,255,255,0.05)',
                    color: form.mood === m ? (MOOD_COLORS[m] || 'var(--cyan)') : 'var(--text3)',
                    border: `1px solid ${form.mood === m ? (MOOD_COLORS[m] || 'var(--cyan)') + '66' : 'transparent'}`,
                    transition: 'all 0.15s',
                  }}>{m}</button>
              ))}
            </div>
          </Field>

          {/* Energy slider */}
          <Field label={<span>Energy <strong style={{ color: 'var(--cyan)' }}>{form.energy}</strong></span>}>
            <div style={{ position: 'relative', marginTop: 8 }}>
              <input type="range" min="0" max="1" step="0.05" value={form.energy}
                onChange={e => set('energy', parseFloat(e.target.value))}
                aria-label="Energy level"
                style={{ width: '100%', accentColor: 'var(--cyan)', cursor: 'pointer' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text3)', marginTop: 2 }}>
                <span>chill</span><span>intense</span>
              </div>
            </div>
          </Field>

          {/* Genre */}
          <Field label="Genre">
            <select className="input" value={form.genre} onChange={e => set('genre', e.target.value)} aria-label="Genre preference"
              style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E\")", backgroundRepeat: 'no-repeat', backgroundPosition: 'right 10px center', paddingRight: 28 }}>
              {GENRES.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
          </Field>

          {/* Context */}
          <Field label="Listening Context">
            <select className="input" value={form.context} onChange={e => set('context', e.target.value)} aria-label="Listening context"
              style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E\")", backgroundRepeat: 'no-repeat', backgroundPosition: 'right 10px center', paddingRight: 28 }}>
              {CONTEXTS.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </Field>

          {/* Results count */}
          <Field label={<span>Results <strong style={{ color: 'var(--cyan)' }}>{form.k}</strong></span>}>
            <input type="range" min="1" max="10" step="1" value={form.k}
              onChange={e => set('k', parseInt(e.target.value))}
              aria-label="Number of results"
              style={{ width: '100%', accentColor: 'var(--cyan)', cursor: 'pointer', marginTop: 8 }} />
          </Field>

          <button onClick={submit} disabled={loading} className="btn" aria-busy={loading}>
            {loading ? <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}><span className="anim-spin">◌</span> Finding…</span> : '🎵 Get Recommendations'}
          </button>

          {error && <p role="alert" style={{ color: '#f87171', fontSize: 12, textAlign: 'center' }}>{error}</p>}
        </div>
      </aside>

      {/* ── Results ── */}
      <section aria-label="Recommendations">
        {results ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
              <p style={{ fontWeight: 800, fontSize: 15, color: 'var(--text)' }}>🎶 Your Playlist</p>
              <span style={{ fontSize: 11, color: 'var(--text3)' }}>{results.songs.length} tracks</span>
            </div>
            <div className="stagger">
              {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} style={{ marginBottom: 10 }} />)}
            </div>
          </div>
        ) : (
          <div className="card anim-fade-in" style={{ padding: 48, textAlign: 'center', color: 'var(--text3)' }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🎵</div>
            <p style={{ fontWeight: 600, fontSize: 14, marginBottom: 6, color: 'var(--text2)' }}>Set your preferences</p>
            <p style={{ fontSize: 13 }}>Choose your mood, energy, and genre on the left, then click Get Recommendations.</p>
          </div>
        )}
      </section>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: 12, color: 'var(--text2)', fontWeight: 600, marginBottom: 4 }}>{label}</label>
      {children}
    </div>
  )
}
