import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Sparkles, ArrowRight, Zap, Scissors, Film, PlaySquare } from 'lucide-react'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError('')
    try {
      const res = await api.post('/jobs', { url })
      const jobId = res.data.id
      navigate(`/job/${jobId}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start clipping job.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col justify-center items-center px-6 py-16 max-w-6xl mx-auto w-full text-center relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-red-600/15 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-600/15 rounded-full blur-[120px] pointer-events-none" />

      <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-red-400 text-xs font-semibold uppercase tracking-wider mb-8 backdrop-blur-xl shadow-lg shadow-red-500/5 animate-pulse">
        <Sparkles size={14} /> AI-Powered Short & Reel Studio
      </div>

      <h2 className="text-5xl md:text-7xl lg:text-8xl font-extrabold mb-8 tracking-tighter leading-[1.05]">
        Create viral clips with <span className="bg-gradient-to-r from-red-500 via-rose-400 to-purple-600 bg-clip-text text-transparent">zero effort</span>.
      </h2>
      <p className="text-gray-400 text-lg md:text-xl mb-14 max-w-2xl mx-auto font-normal leading-relaxed">
        Transform long YouTube videos into 9:16 vertical clips. Powered by automated highlight detection, audio energy scoring, and word-level animated subtitles.
      </p>

      <form onSubmit={handleSubmit} className="w-full max-w-2xl flex flex-col sm:flex-row gap-3 bg-gray-900/60 border border-white/10 p-2.5 rounded-2xl shadow-2xl backdrop-blur-2xl">
        <div className="relative flex-1 flex items-center">
          <PlaySquare className="absolute left-4 text-gray-400" size={20} />
          <input
            type="url"
            placeholder="Paste YouTube link (e.g. https://youtu.be/...)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full pl-12 pr-4 py-4 rounded-xl bg-transparent focus:outline-none text-white placeholder-gray-500 text-sm font-medium"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-8 py-4 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 font-bold text-white transition-all disabled:opacity-50 shadow-xl shadow-red-600/25 flex items-center justify-center gap-2 text-sm tracking-wide cursor-pointer"
        >
          {loading ? (
            <>Processing...</>
          ) : (
            <>
              Generate Shorts <ArrowRight size={16} />
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-950/80 border border-red-800 text-red-200 rounded-2xl max-w-md mx-auto text-sm">
          {error}
        </div>
      )}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 w-full text-left">
        <div className="p-8 rounded-3xl bg-gray-900/40 border border-white/5 backdrop-blur-xl hover:border-white/10 transition group">
          <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 mb-6 group-hover:scale-110 transition duration-300">
            <Zap size={22} />
          </div>
          <h3 className="font-bold text-lg mb-2 text-white tracking-tight">Smart Highlight Engine</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Combines YouTube heatmap retention peaks and audio excitement spikes to isolate maximum engagement moments.
          </p>
        </div>

        <div className="p-8 rounded-3xl bg-gray-900/40 border border-white/5 backdrop-blur-xl hover:border-white/10 transition group">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-6 group-hover:scale-110 transition duration-300">
            <Scissors size={22} />
          </div>
          <h3 className="font-bold text-lg mb-2 text-white tracking-tight">9:16 Vertical Reframing</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Automatically crops and centers widescreen footage into professional 1080x1920 vertical videos ready for TikTok & Reels.
          </p>
        </div>

        <div className="p-8 rounded-3xl bg-gray-900/40 border border-white/5 backdrop-blur-xl hover:border-white/10 transition group">
          <div className="w-12 h-12 rounded-2xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-6 group-hover:scale-110 transition duration-300">
            <Film size={22} />
          </div>
          <h3 className="font-bold text-lg mb-2 text-white tracking-tight">Animated Subtitles</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Powered by `faster-whisper` word timestamps with custom font styling and burned-in dynamic captions.
          </p>
        </div>
      </div>
    </div>
  )
}
