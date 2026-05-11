import { useState } from 'react'
import { recommendByProfile } from '../api'
import SongCard from './SongCard'

const MOODS = ['happy', 'sad', 'chill', 'intense', 'focused', 'moody', 'relaxed']
const GENRES = ['pop', 'rock', 'jazz', 'lofi', 'house', 'synthwave', 'indie', 'ambient', 'r&b', 'folk']
const CONTEXTS = ['general', 'study', 'workout', 'party', 'relax', 'night', 'drive', 'coffee']

export default function ProfileTab({ sessionId, onSession }) {
  const [form, setForm] = useState({
    mood: 'happy', energy: 0.7, genre: 'pop',
    vocal: 'vocal', context: 'general', k: 5,
  })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async () => {
    setLoading(true); setError(null)
    try {
      const data = await recommendByProfile({ ...form, session_id: sessionId })
      setResults(data)
      onSession(data.session_id)
    } catch (e) {
      setError('Failed to get recommendations. Is the API running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Form */}
      <div className="space-y-5">
        <h2 className="text-lg font-semibold text-white">Your Preferences</h2>

        <Field label="Mood">
          <select className={select} value={form.mood} onChange={e => set('mood', e.target.value)}>
            {MOODS.map(m => <option key={m}>{m}</option>)}
          </select>
        </Field>

        <Field label={`Energy — ${form.energy}`}>
          <input type="range" min="0" max="1" step="0.05" value={form.energy}
            onChange={e => set('energy', parseFloat(e.target.value))}
            className="w-full accent-cyan-500" />
        </Field>

        <Field label="Genre">
          <select className={select} value={form.genre} onChange={e => set('genre', e.target.value)}>
            {GENRES.map(g => <option key={g}>{g}</option>)}
          </select>
        </Field>

        <Field label="Listening Context">
          <select className={select} value={form.context} onChange={e => set('context', e.target.value)}>
            {CONTEXTS.map(c => <option key={c}>{c}</option>)}
          </select>
        </Field>

        <Field label={`Results — ${form.k}`}>
          <input type="range" min="1" max="10" step="1" value={form.k}
            onChange={e => set('k', parseInt(e.target.value))}
            className="w-full accent-cyan-500" />
        </Field>

        <button onClick={submit} disabled={loading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          {loading ? 'Finding songs…' : '🎵 Get Recommendations'}
        </button>

        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>

      {/* Results */}
      <div>
        {results ? (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Your Playlist</h2>
            {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} />)}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Set your preferences and click Get Recommendations
          </div>
        )}
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1.5">{label}</label>
      {children}
    </div>
  )
}

const select = "w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500/60"
