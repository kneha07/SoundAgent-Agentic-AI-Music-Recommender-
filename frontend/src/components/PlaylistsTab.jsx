import { useState } from 'react'
import { recommendByNL } from '../api'
import SongCard from './SongCard'

const PLAYLISTS = [
  { name: 'Party Starter', emoji: '🎉', query: 'upbeat party music happy electronic pop high energy', desc: 'High-energy bangers to get the crowd moving' },
  { name: 'Deep Focus', emoji: '🧠', query: 'calm study songs chill instrumental dreamy focus', desc: 'Calm, instrumental-friendly tracks for studying' },
  { name: 'Pump Up', emoji: '💪', query: 'intense workout tracks strong rock aggressive driving energy', desc: 'Intense, driving tracks to push your workout harder' },
  { name: 'Night Vibes', emoji: '🌙', query: 'moody atmospheric night music emotional vocal dark', desc: 'Moody, atmospheric songs for late nights' },
  { name: 'Morning Energy', emoji: '☀️', query: 'bright uplifting morning pop happy energetic start day', desc: 'Bright, uplifting tracks to start your day right' },
  { name: 'Coffee Shop', emoji: '☕', query: 'easy acoustic chill relaxed coffee afternoon lofi jazz', desc: 'Easy-going acoustic vibes for a relaxed afternoon' },
]

export default function PlaylistsTab({ sessionId, onSession }) {
  const [active, setActive] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(null)

  const play = async (pl) => {
    setActive(pl.name); setLoading(pl.name)
    const data = await recommendByNL({ query: pl.query, session_id: sessionId, k: 5 })
    setResults({ ...data, name: pl.name })
    onSession(data.session_id)
    setLoading(null)
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {PLAYLISTS.map(pl => (
          <button key={pl.name} onClick={() => play(pl)}
            className={`text-left p-5 rounded-2xl border transition-all ${
              active === pl.name
                ? 'border-cyan-500/60 bg-cyan-500/10'
                : 'border-white/10 bg-white/5 hover:border-cyan-500/30 hover:bg-white/8'
            }`}>
            <div className="text-2xl mb-2">{pl.emoji}</div>
            <p className="font-semibold text-white">{pl.name}</p>
            <p className="text-xs text-slate-400 mt-1">{pl.desc}</p>
            <div className="mt-3">
              <span className="text-xs px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400">
                {loading === pl.name ? 'Loading…' : 'Play'}
              </span>
            </div>
          </button>
        ))}
      </div>

      {results && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">{results.name}</h2>
          {results.songs.map((s, i) => <SongCard key={i} song={s} rank={i + 1} />)}
        </div>
      )}
    </div>
  )
}
