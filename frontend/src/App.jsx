import { useState, useEffect } from 'react'
import { getCatalog } from './api'
import ProfileTab from './components/ProfileTab'
import NLTab from './components/NLTab'
import PlaylistsTab from './components/PlaylistsTab'
import './index.css'

const TABS = [
  { id: 'profile',   icon: '⚙️', label: 'Profile Builder' },
  { id: 'nl',        icon: '💬', label: 'Natural Language' },
  { id: 'playlists', icon: '🎧', label: 'Playlists' },
]

const STATS = [
  { icon: '🎵', key: 'total',    label: 'Songs',    color: '#06b6d4' },
  { icon: '🎸', key: 'genres',   label: 'Genres',   color: '#22d3ee' },
  { icon: '🌈', key: 'moods',    label: 'Moods',    color: '#10b981' },
  { icon: '📍', key: 'contexts', label: 'Contexts', color: '#f59e0b' },
]

export default function App() {
  const [tab, setTab] = useState('profile')
  const [catalog, setCatalog] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  useEffect(() => { getCatalog().then(setCatalog).catch(() => {}) }, [])

  const val = k => catalog ? (Array.isArray(catalog[k]) ? catalog[k].length : catalog[k]) : '—'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>

      {/* ── Hero ── */}
      <header style={{
        position: 'relative', overflow: 'hidden',
        background: 'linear-gradient(135deg, #0a1628 0%, #0c2d48 50%, #0e3d5c 100%)',
        borderBottom: '1px solid rgba(6,182,212,0.15)',
      }}>
        {/* Glow orbs */}
        <div style={{ position:'absolute', top:-120, right:-100, width:500, height:500, borderRadius:'50%', background:'radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 65%)', pointerEvents:'none' }} />
        <div style={{ position:'absolute', bottom:-80, left:'20%', width:350, height:350, borderRadius:'50%', background:'radial-gradient(circle, rgba(8,145,178,0.12) 0%, transparent 65%)', pointerEvents:'none' }} />

        <div style={{ maxWidth:940, margin:'0 auto', padding:'40px 40px 36px', position:'relative' }}>
          {/* Logo */}
          <div className="anim-fade-up" style={{ display:'flex', alignItems:'center', gap:14, marginBottom:28 }}>
            <div className="anim-float" style={{
              width:54, height:54, borderRadius:16, flexShrink:0,
              background:'linear-gradient(135deg, #0891b2, #06b6d4)',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:26, boxShadow:'0 6px 28px rgba(6,182,212,0.5)',
            }}>🎵</div>
            <div>
              <h1 className="grad-text" style={{ fontSize:30, fontWeight:900, letterSpacing:'-0.5px', lineHeight:1.1 }}>SoundAgent</h1>
              <p style={{ color:'#a5f3fc', fontSize:13, marginTop:3, opacity:.85 }}>AI-powered music · mood · energy · context</p>
            </div>
          </div>

          {/* Stat cards */}
          {catalog && (
            <div className="stagger" style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12 }}>
              {STATS.map(s => (
                <div key={s.key} className="anim-fade-up" style={{
                  background: 'rgba(255,255,255,0.07)',
                  border: `1px solid ${s.color}30`,
                  borderTop: `3px solid ${s.color}`,
                  borderRadius: 14, padding:'16px 14px', textAlign:'center',
                  transition: 'transform .2s, box-shadow .2s', cursor:'default',
                }}
                  onMouseEnter={e => { e.currentTarget.style.transform='translateY(-4px)'; e.currentTarget.style.boxShadow=`0 8px 28px ${s.color}30` }}
                  onMouseLeave={e => { e.currentTarget.style.transform=''; e.currentTarget.style.boxShadow='' }}
                >
                  <div style={{ fontSize:22, marginBottom:6 }}>{s.icon}</div>
                  <p style={{ fontSize:28, fontWeight:900, color:s.color, lineHeight:1 }}>{val(s.key)}</p>
                  <p style={{ fontSize:10, color:'rgba(255,255,255,0.5)', marginTop:5, fontWeight:600, textTransform:'uppercase', letterSpacing:'0.6px' }}>{s.label}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* ── Tabs ── */}
      <div style={{ background:'var(--card)', borderBottom:'1px solid var(--border)', position:'sticky', top:0, zIndex:10 }}>
        <div style={{ maxWidth:940, margin:'0 auto', padding:'0 40px', display:'flex' }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              role="tab" aria-selected={tab === t.id}
              style={{
                padding:'14px 20px', border:'none', cursor:'pointer',
                background:'transparent',
                borderBottom: `3px solid ${tab===t.id ? 'var(--cyan)' : 'transparent'}`,
                color: tab===t.id ? 'var(--cyan)' : 'var(--text3)',
                fontSize:13, fontWeight:600, fontFamily:'inherit',
                display:'flex', alignItems:'center', gap:6,
                transition:'all .2s', marginBottom:-1,
              }}
              onMouseEnter={e => { if(tab!==t.id) e.currentTarget.style.color='var(--text2)' }}
              onMouseLeave={e => { if(tab!==t.id) e.currentTarget.style.color='var(--text3)' }}
            >{t.icon} {t.label}</button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      <main style={{ maxWidth:940, margin:'0 auto', padding:'32px 40px 60px' }}>
        {tab === 'profile'   && <ProfileTab   sessionId={sessionId} onSession={setSessionId} />}
        {tab === 'nl'        && <NLTab        sessionId={sessionId} onSession={setSessionId} />}
        {tab === 'playlists' && <PlaylistsTab sessionId={sessionId} onSession={setSessionId} />}
      </main>

      <footer style={{ borderTop:'1px solid var(--border)', padding:'16px 40px', textAlign:'center', fontSize:12, color:'var(--text3)' }}>
        SoundAgent — Powered by <span style={{ color:'var(--cyan)', fontWeight:600 }}>Claude AI</span>
        {sessionId && <span style={{ marginLeft:14, fontFamily:'monospace', color:'var(--text3)' }}>session {sessionId.slice(0,8)}</span>}
      </footer>
    </div>
  )
}
