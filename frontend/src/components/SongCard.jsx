import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

let currentAudio = null
let currentSetter = null

export default function SongCard({ song, rank }) {
  const pct   = Math.round(song.score * 100)
  const color = pct >= 80 ? '#06b6d4' : pct >= 65 ? '#10b981' : '#f59e0b'

  const [state, setState]       = useState('idle')
  const [progress, setProgress] = useState(0)
  const [cover, setCover]       = useState(null)
  const [hovered, setHovered]   = useState(false)
  const audioRef = useRef(null)

  useEffect(() => () => audioRef.current?.pause(), [])

  const toggle = async () => {
    if (state === 'loading') return
    if (currentAudio && currentAudio !== audioRef.current) {
      currentAudio.pause(); if (currentSetter) currentSetter('paused')
    }
    if (audioRef.current) {
      if (state === 'playing') { audioRef.current.pause(); setState('paused') }
      else { audioRef.current.play(); setState('playing'); currentAudio = audioRef.current; currentSetter = setState }
      return
    }
    setState('loading')
    try {
      const { data } = await axios.get(`/api/preview?title=${encodeURIComponent(song.title)}&artist=${encodeURIComponent(song.artist)}`)
      setCover(data.album_cover)
      const audio = new Audio(data.preview_url)
      audioRef.current = audio; currentAudio = audio; currentSetter = setState
      audio.addEventListener('timeupdate', () => setProgress(audio.currentTime / 30))
      audio.addEventListener('ended', () => { setState('idle'); setProgress(0) })
      await audio.play(); setState('playing')
    } catch { setState('error'); setTimeout(() => setState('idle'), 2000) }
  }

  const playing = state === 'playing'

  return (
    <article
      className="anim-fade-up"
      aria-label={`${song.title} by ${song.artist} — ${pct}% match`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: playing ? `linear-gradient(135deg, rgba(6,182,212,0.12), var(--card2))` : hovered ? 'var(--card2)' : 'var(--card)',
        border: `1px solid ${playing ? 'rgba(6,182,212,0.4)' : hovered ? 'var(--border2)' : 'var(--border)'}`,
        borderLeft: `4px solid ${color}`,
        borderRadius: 'var(--radius)',
        padding: '14px 16px',
        marginBottom: 10,
        boxShadow: playing ? '0 4px 20px rgba(6,182,212,0.2)' : hovered ? '0 4px 16px rgba(0,0,0,0.3)' : 'var(--shadow-card)',
        transition: 'all .22s ease',
        transform: hovered && !playing ? 'translateX(4px)' : 'none',
      }}
    >
      <div style={{ display:'flex', alignItems:'center', gap:10 }}>
        {/* Play button */}
        <button onClick={toggle}
          aria-label={playing ? `Pause ${song.title}` : `Play preview of ${song.title}`}
          style={{
            width:38, height:38, borderRadius:'50%', border:'none', cursor:'pointer', flexShrink:0,
            background: playing ? `linear-gradient(135deg, var(--teal), var(--cyan))` : state === 'error' ? '#ef4444' : 'rgba(255,255,255,0.1)',
            color:'#fff', fontSize:state === 'loading' ? 10 : 13,
            display:'flex', alignItems:'center', justifyContent:'center',
            transition:'all .2s',
            boxShadow: playing ? '0 0 16px rgba(6,182,212,0.6)' : 'none',
          }}>
          {state === 'loading' ? <span className="anim-spin" style={{display:'block',width:14,height:14,border:'2px solid rgba(255,255,255,0.3)',borderTopColor:'#fff',borderRadius:'50%'}} />
            : playing ? '⏸' : state === 'paused' ? '▶' : state === 'error' ? '✕' : '▶'}
        </button>

        {/* Art / rank */}
        {cover
          ? <img src={cover} alt="" style={{ width:38,height:38,borderRadius:8,objectFit:'cover',flexShrink:0,boxShadow:'0 2px 8px rgba(0,0,0,0.5)' }} />
          : <div style={{ width:30,height:30,borderRadius:'50%',flexShrink:0,background:`${color}25`,color,fontSize:11,fontWeight:800,display:'flex',alignItems:'center',justifyContent:'center' }}>#{rank}</div>
        }

        {/* Title */}
        <div style={{ flex:1, minWidth:0 }}>
          <p style={{ fontWeight:700, color:'var(--text)', fontSize:14, margin:0, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{song.title}</p>
          <p style={{ color:'var(--text2)', fontSize:12, margin:'2px 0 0', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{song.artist}</p>
        </div>

        {/* Score */}
        <div style={{ padding:'4px 10px', borderRadius:20, background:`${color}18`, border:`1px solid ${color}44`, color, fontSize:12, fontWeight:800, flexShrink:0 }}>{pct}%</div>
      </div>

      {/* Bar */}
      <div style={{ height:3, background:'rgba(255,255,255,0.06)', borderRadius:4, marginTop:12, overflow:'hidden', cursor: (playing || state==='paused') ? 'pointer' : 'default' }}
        onClick={e => {
          if (!audioRef.current || (state !== 'playing' && state !== 'paused')) return
          audioRef.current.currentTime = ((e.clientX - e.currentTarget.getBoundingClientRect().left) / e.currentTarget.offsetWidth) * 30
        }}>
        <div style={{
          height:'100%', borderRadius:4, transition: playing ? 'width .5s linear' : 'width .6s ease',
          width: `${(playing||state==='paused') ? progress*100 : pct}%`,
          background: (playing||state==='paused') ? `linear-gradient(90deg, var(--teal), var(--cyan))` : `linear-gradient(90deg, ${color}, var(--teal))`,
          animation: state === 'idle' ? 'bar-in .6s ease' : 'none',
        }} />
      </div>

      {/* Tags + links */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:10, flexWrap:'wrap', gap:6 }}>
        <div style={{ display:'flex', flexWrap:'wrap', gap:5 }}>
          {[song.genre, song.mood, song.listening_context !== 'general' ? song.listening_context : null, ...(song.mood_tags||[]).slice(0,2)]
            .filter(Boolean).map((t,i) => (
              <span key={i} style={{ padding:'2px 8px', borderRadius:20, background:'rgba(255,255,255,0.07)', border:'1px solid rgba(255,255,255,0.09)', color:'var(--text2)', fontSize:11, fontWeight:500 }}>{t}</span>
            ))}
        </div>
        <div style={{ display:'flex', gap:6, flexShrink:0, alignItems:'center' }}>
          {playing && <span style={{ fontSize:11, color:'var(--cyan)', fontWeight:600, display:'flex', alignItems:'center', gap:4 }}>
            <span className="anim-pulse" style={{ width:6, height:6, borderRadius:'50%', background:'var(--cyan)', display:'inline-block' }} />30s preview
          </span>}
          {state === 'error' && <span style={{ fontSize:11, color:'#f87171' }}>No preview</span>}
          <a href={`https://www.youtube.com/results?search_query=${encodeURIComponent(song.title+' '+song.artist)}`}
            target="_blank" rel="noreferrer" aria-label={`YouTube: ${song.title}`}
            style={{ padding:'3px 10px', borderRadius:20, fontSize:11, fontWeight:600, background:'rgba(239,68,68,0.12)', color:'#fca5a5', border:'1px solid rgba(239,68,68,0.2)', textDecoration:'none', transition:'background .15s' }}
            onMouseEnter={e => e.currentTarget.style.background='rgba(239,68,68,0.22)'}
            onMouseLeave={e => e.currentTarget.style.background='rgba(239,68,68,0.12)'}
          >▶ YouTube</a>
          <a href={`https://open.spotify.com/search/${encodeURIComponent(song.title+' '+song.artist)}`}
            target="_blank" rel="noreferrer" aria-label={`Spotify: ${song.title}`}
            style={{ padding:'3px 10px', borderRadius:20, fontSize:11, fontWeight:600, background:'rgba(29,185,84,0.12)', color:'#6ee7b7', border:'1px solid rgba(29,185,84,0.2)', textDecoration:'none', transition:'background .15s' }}
            onMouseEnter={e => e.currentTarget.style.background='rgba(29,185,84,0.22)'}
            onMouseLeave={e => e.currentTarget.style.background='rgba(29,185,84,0.12)'}
          >♫ Spotify</a>
        </div>
      </div>
    </article>
  )
}
