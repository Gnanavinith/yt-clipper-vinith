import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import JobPage from './pages/JobPage'
import ClipEditor from './pages/ClipEditor'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <header className="border-b border-gray-800 p-4 bg-gray-900 flex justify-between items-center shadow-md">
        <h1 className="text-xl font-bold bg-gradient-to-r from-red-500 to-purple-500 bg-clip-text text-transparent">
          🎬 YT-Clipper (Shorts & Reels Generator)
        </h1>
        <div className="text-sm text-gray-400">Powered by yt-dlp & Whisper</div>
      </header>
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/job/:jobId" element={<JobPage />} />
          <Route path="/clip/:clipId" element={<ClipEditor />} />
        </Routes>
      </main>
    </div>
  )
}
