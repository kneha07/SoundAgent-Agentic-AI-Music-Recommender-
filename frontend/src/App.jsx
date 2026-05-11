import { useState, useEffect } from 'react'
import { getCatalog } from './api'
import ProfileTab from './components/ProfileTab'
import NLTab from './components/NLTab'
import PlaylistsTab from './components/PlaylistsTab'
import './index.css'

const TABS = [
  { id: 'profile', label: '⚙️ Profile Builder' },
  { id: 'nl', label: '💬 Natural Language' },
  { id: 'playlists', label: '🎧 Playlists' },
]

export default function App() {
  const [tab, setTab] = useState('profile')
  const [catalog, setCatalog] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  useEffect(() => {
    getCatalog().then(setCatalog).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-slate-200">
      {/* Hero */}
      <div className="bg-gradient-to-br from-[#0a1628] via-[#0c2d48] to-[#0e3d5c] px-6 py-10">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">🎵</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">SoundAgent</h1>
          </div>
          <p className="text-cyan-300 text-sm">AI-powered music recommendations tailored to your mood, energy, and listening context</p>

          {catalog && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
              {[
                { label: 'Songs in catalog', value: catalog.total },
                { label: 'Genres available', value: catalog.genres.length },
                { label: 'Mood categories', value: catalog.moods.length },
                { label: 'Listening contexts', value: catalog.contexts.length },
              ].map(s => (
                <div key={s.label} className="bg-white/10 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-cyan-400">{s.value}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-4xl mx-auto px-6">
        <div className="flex gap-1 border-b border-white/10 mt-6">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all ${
                tab === t.id
                  ? 'text-cyan-400 border-b-2 border-cyan-400 bg-white/5'
                  : 'text-slate-400 hover:text-white'
              }`}>
              {t.label}
            </button>
          ))}
        </div>

        <div className="py-8">
          {tab === 'profile' && <ProfileTab sessionId={sessionId} onSession={setSessionId} />}
          {tab === 'nl' && <NLTab sessionId={sessionId} onSession={setSessionId} />}
          {tab === 'playlists' && <PlaylistsTab sessionId={sessionId} onSession={setSessionId} />}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 py-6 mt-4 text-center text-xs text-slate-500">
        SoundAgent — Powered by Claude AI
        {sessionId && <span className="ml-3 text-slate-600">Session: {sessionId.slice(0, 8)}</span>}
      </div>
    </div>
  )
}
