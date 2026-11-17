import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { Loader2, CheckCircle2, AlertCircle, Download, Edit3, Film, ArrowLeft } from 'lucide-react'

export default function JobPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let interval = setInterval(async () => {
      try {
        const res = await api.get(`/jobs/${jobId}`)
        setJob(res.data)
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          clearInterval(interval)
        }
      } catch (err) {
        setError('Failed to fetch job status.')
        clearInterval(interval)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [jobId])

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <AlertCircle className="text-red-500 w-12 h-12 mb-4" />
        <h3 className="text-xl font-bold mb-2">Error Occurred</h3>
        <p className="text-gray-400 mb-6">{error}</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-xl font-semibold transition flex items-center gap-2"
        >
          <ArrowLeft size={16} /> Back to Home
        </button>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-400">
        <Loader2 className="animate-spin w-8 h-8 text-red-500 mb-3" />
        Loading job pipeline status...
      </div>
    )
  }

  return (
    <div className="flex-1 p-6 md:p-10 max-w-6xl mx-auto w-full">
      <button
        onClick={() => navigate('/')}
        className="mb-6 inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition"
      >
        <ArrowLeft size={16} /> Back to Generator
      </button>

      {/* Progress Card */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-3xl p-8 shadow-2xl backdrop-blur-md mb-12">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-1">Processing YouTube Video</h2>
            <p className="text-sm text-gray-400 truncate max-w-xl">URL: {job.url}</p>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-gray-800 border border-gray-700 text-sm font-semibold uppercase tracking-wider">
            {job.status === 'completed' ? (
              <CheckCircle2 className="text-green-500 w-4 h-4" />
            ) : job.status === 'failed' ? (
              <AlertCircle className="text-red-500 w-4 h-4" />
            ) : (
              <Loader2 className="animate-spin text-yellow-500 w-4 h-4" />
            )}
            <span className={
              job.status === 'completed' ? 'text-green-400' :
              job.status === 'failed' ? 'text-red-400' : 'text-yellow-400'
            }>
              {job.status}
            </span>
          </div>
        </div>

        <div className="w-full bg-gray-800 rounded-full h-3 mb-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-red-500 to-pink-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${job.progress}%` }}
          />
        </div>
        <div className="flex justify-between text-sm text-gray-400">
          <span>Pipeline Stage Progress</span>
          <span className="font-bold text-white">{job.progress}%</span>
        </div>

        {job.error && (
          <div className="mt-6 p-4 bg-red-950/80 border border-red-800 text-red-200 rounded-xl">
            {job.error}
          </div>
        )}
      </div>

      {/* Clips Grid */}
      {job.status === 'completed' && (
        <div>
          <div className="flex items-center gap-3 mb-6">
            <Film className="text-red-500" size={24} />
            <h3 className="text-2xl font-bold">Generated Viral Clips ({job.clips.length})</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {job.clips.map((clip) => (
              <div key={clip.id} className="bg-gray-900/90 border border-gray-800 rounded-3xl overflow-hidden shadow-xl flex flex-col group hover:border-gray-700 transition">
                <div className="aspect-[9/16] bg-black relative flex items-center justify-center overflow-hidden">
                  <video
                    src={clip.video_url || `/storage/clips/${job.id}/clip_${clip.id.split('_').pop()}.mp4`}
                    controls
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-3 right-3 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-xs font-semibold text-white">
                    Score: {clip.score.toFixed(2)}
                  </div>
                </div>

                <div className="p-5 flex flex-col flex-1 justify-between gap-4">
                  <div>
                    <h4 className="font-bold text-base mb-1 text-white line-clamp-1">{clip.title || 'Highlight Clip'}</h4>
                    <p className="text-xs text-gray-400">
                      Duration: {Math.round(clip.end_time - clip.start_time)}s ({Math.round(clip.start_time)}s - {Math.round(clip.end_time)}s)
                    </p>
                  </div>

                  <div className="flex items-center gap-2 pt-2 border-t border-gray-800">
                    <button
                      onClick={() => navigate(`/clip/${clip.id}`)}
                      className="flex-1 py-2.5 px-4 bg-gray-800 hover:bg-gray-700 rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <Edit3 size={16} /> Edit
                    </button>
                    <a
                      href={`/api/clips/${clip.id}/download`}
                      className="flex-1 py-2.5 px-4 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 rounded-xl font-semibold text-sm text-center transition shadow-md shadow-red-600/30 flex items-center justify-center gap-2 cursor-pointer"
                      download
                    >
                      <Download size={16} /> Download
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
