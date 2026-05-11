import { useState } from 'react'
import { recommendByNL } from '../api'
import SongCard from './SongCard'

const SAMPLES = [
  'Upbeat party music for a happy listener who loves electronic pop',
  'Calm study songs with a chill mood and dreamy textures',
  'Intense workout tracks with strong rock energy',
  'Sad but powerful night music that is emotional and vocal-heavy',
]

export default function NLTab({ sessionId, onSession }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const submit = async (q) => {
    const text = q || query
    if (!text.trim()) return
    setLoading(true); setError(null)
    try {
      const data = await recommendByNL({ query: text, session_id: sessionId, k: 5 })
      setResults(data)
      onSession(data.session_id)
    } catch (e) {
      setError('Failed to get recommendations. Is the API running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Sample prompts */}
      <div>
        <p className="text-sm text-slate-400 mb-2">Try a sample prompt:</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {SAMPLES.map(s => (
            <button key={s} onClick={() => { setQuery(s); submit(s) }}
              className="text-left text-sm px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 hover:border-cyan-500/40 hover:text-white transition truncate">
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="space-y-3">
        <textarea
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), submit())}
          placeholder="Describe your ideal playlist…"
          rows={3}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm resize-none focus:outline-none focus:border-cyan-500/60 placeholder-slate-500"
        />
        <button onClick={() => submit()} disabled={loading || !query.trim()}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          {loading ? 'Finding songs…' : '🔍 Find My Songs'}
        </button>
        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-white">Your Playlist</h2>
            {results.confidence && (
              <span className="text-xs px-3 py-1 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                {Math.round(results.confidence * 100)}% confidence
              </span>
            )}
            {results.mode && (
              <span className="text-xs px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                {results.mode}
              </span>
            )}
          </div>

          {results.explanation && (
            <div className="bg-white/5 border border-cyan-500/20 rounded-xl p-4 text-sm text-slate-300 italic">
              {results.explanation}
            </div>
          )}

          <div className="space-y-3">
            {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} />)}
          </div>
        </div>
      )}
    </div>
  )
}
