export default function SongCard({ song, rank }) {
  const pct = Math.round(song.score * 100)
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:border-cyan-500/40 hover:bg-white/8 transition-all">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <span className="w-8 h-8 rounded-full bg-cyan-500/20 text-cyan-400 text-sm font-bold flex items-center justify-center shrink-0">
            {rank}
          </span>
          <div className="min-w-0">
            <p className="font-semibold text-white truncate">{song.title}</p>
            <p className="text-sm text-slate-400 truncate">{song.artist}</p>
          </div>
        </div>
        <span className="text-cyan-400 font-bold text-sm shrink-0">{pct}%</span>
      </div>

      <div className="mt-3">
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        <Tag>{song.genre}</Tag>
        <Tag>{song.mood}</Tag>
        {song.listening_context && song.listening_context !== 'general' && (
          <Tag>{song.listening_context}</Tag>
        )}
        {song.mood_tags?.slice(0, 3).map(t => <Tag key={t}>{t}</Tag>)}
      </div>
    </div>
  )
}

function Tag({ children }) {
  return (
    <span className="px-2 py-0.5 rounded-full text-xs bg-white/10 text-slate-300">
      {children}
    </span>
  )
}
