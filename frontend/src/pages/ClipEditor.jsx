import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { ArrowLeft, Download, Sliders, Sparkles, Check, Loader2 } from 'lucide-react'

export default function ClipEditor() {
  const { clipId } = useParams()
  const navigate = useNavigate()
  const [clip, setClip] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState(0)
  const [endTime, setEndTime] = useState(0)
  const [captionStyle, setCaptionStyle] = useState('default')
  const [subtitles, setSubtitles] = useState([])

  useEffect(() => {
    fetchClip()
  }, [clipId])

  const fetchClip = async () => {
    try {
      const res = await api.get(`/clips/${clipId}`)
      setClip(res.data)
      setTitle(res.data.title || '')
      setStartTime(res.data.start_time)
      setEndTime(res.data.end_time)
      setCaptionStyle(res.data.caption_style || 'default')
      setSubtitles(res.data.subtitles || [])
    } catch (err) {
      setError('Failed to load clip details.')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSuccessMsg('')
    try {
      await api.patch(`/clips/${clipId}`, {
        title,
        start_time: parseFloat(startTime),
        end_time: parseFloat(endTime),
        caption_style: captionStyle,
        subtitles,
      })
      setSuccessMsg('Clip updated and re-rendered successfully!')
      // Refresh clip data to reload video player cache
      await fetchClip()
    } catch (err) {
      setError('Failed to save clip updates.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
        <Loader2 className="animate-spin w-8 h-8 text-red-500 mb-3" />
        Loading clip editor...
      </div>
    )
  }

  if (error && !clip) {
    return <div className="p-8 text-center text-red-500">{error}</div>
  }

  return (
    <div className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition cursor-pointer"
      >
        <ArrowLeft size={16} /> Back to Job Clips
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Video Preview Column */}
        <div className="lg:col-span-5 flex flex-col items-center bg-gray-900/80 border border-gray-800 p-6 rounded-3xl shadow-2xl backdrop-blur-md sticky top-6">
          <div className="flex items-center justify-between w-full mb-4">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <Sparkles size={18} className="text-red-500" /> 9:16 Preview
            </h3>
            <span className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold">
              Shorts Ready
            </span>
          </div>

          <div className="w-full max-w-[280px] aspect-[9/16] bg-black rounded-2xl overflow-hidden shadow-2xl border border-gray-800 flex items-center justify-center mb-6">
            <video
              key={clip.file_path}
              src={clip.video_url || `/storage/clips/${clip.job_id}/${clip.id.split('_').pop()}.mp4?t=${Date.now()}`}
              controls
              className="w-full h-full object-contain"
            />
          </div>

          <a
            href={`/api/clips/${clip.id}/download`}
            className="w-full py-4 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 rounded-2xl font-bold text-center transition shadow-lg shadow-red-600/30 flex items-center justify-center gap-2 cursor-pointer text-white"
            download
          >
            <Download size={18} /> Download Final MP4
          </a>
        </div>

        {/* Editor Controls Column */}
        <div className="lg:col-span-7 bg-gray-900/80 border border-gray-800 p-8 rounded-3xl shadow-2xl backdrop-blur-md flex flex-col gap-6">
          <div className="flex items-center gap-3 pb-6 border-b border-gray-800">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
              <Sliders size={20} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Clip Customization</h3>
              <p className="text-xs text-gray-400">Trim duration, update title, or change caption styling</p>
            </div>
          </div>

          {error && <div className="p-4 bg-red-950/80 border border-red-800 text-red-200 rounded-xl">{error}</div>}
          {successMsg && (
            <div className="p-4 bg-green-950/80 border border-green-800 text-green-200 rounded-xl flex items-center gap-2">
              <Check size={18} /> {successMsg}
            </div>
          )}

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-300">Clip Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="p-4 rounded-xl bg-gray-800/80 border border-gray-700 focus:border-red-500 focus:outline-none text-white text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold text-gray-300">Start Time (seconds)</label>
              <input
                type="number"
                step="0.1"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="p-4 rounded-xl bg-gray-800/80 border border-gray-700 focus:border-red-500 focus:outline-none text-white text-sm"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-semibold text-gray-300">End Time (seconds)</label>
              <input
                type="number"
                step="0.1"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="p-4 rounded-xl bg-gray-800/80 border border-gray-700 focus:border-red-500 focus:outline-none text-white text-sm"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-300">Caption Style Preset</label>
            <select
              value={captionStyle}
              onChange={(e) => setCaptionStyle(e.target.value)}
              className="p-4 rounded-xl bg-gray-800/80 border border-gray-700 focus:border-red-500 focus:outline-none text-white text-sm cursor-pointer"
            >
              <option value="default">Default Poppins (Yellow Highlight)</option>
              <option value="bold">Bold White / Black Outline</option>
              <option value="neon">Neon Glow Accent</option>
            </select>
          </div>

          <div className="pt-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 rounded-2xl font-bold text-white transition disabled:opacity-50 shadow-lg shadow-green-600/30 flex items-center justify-center gap-2 cursor-pointer text-base"
            >
              {saving ? (
                <>
                  <Loader2 className="animate-spin" size={18} /> Re-rendering Video...
                </>
              ) : (
                <>
                  <Check size={18} /> Save & Re-render Clip
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
