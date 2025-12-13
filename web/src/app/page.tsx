'use client'

import dynamic from 'next/dynamic'
import Link from 'next/link'
import { Suspense, useState, useEffect } from 'react'

// Dynamic import to avoid SSR issues with Three.js
const QuantumScene = dynamic(() => import('@/components/QuantumScene'), {
  ssr: false,
  loading: () => <div className="loading">Initializing quantum interface...</div>
})

interface HeartbeatData {
  beat_number: number
  timestamp_utc: string
  coherence_estimate: number
  entropy: number
  dominant_state: string
  counts: Record<string, number>
}

export default function Home() {
  const [heartbeatData, setHeartbeatData] = useState<HeartbeatData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load latest heartbeat data
    fetch('/api/heartbeat/latest')
      .then(res => res.json())
      .then(data => {
        setHeartbeatData(data)
        setLoading(false)
      })
      .catch(() => {
        // Fallback to sample data if API not available
        setHeartbeatData({
          beat_number: 0,
          timestamp_utc: new Date().toISOString(),
          coherence_estimate: 0.85,
          entropy: 0.15,
          dominant_state: '00000',
          counts: {
            '00000': 870,
            '10000': 55,
            '01000': 35,
            '00100': 20,
            '00010': 12,
            '00001': 8
          }
        })
        setLoading(false)
      })
  }, [])

  return (
    <main style={{ height: '100vh', position: 'relative' }}>
      {/* 3D Scene */}
      <Suspense fallback={<div className="loading">Loading...</div>}>
        <QuantumScene heartbeatData={heartbeatData} />
      </Suspense>

      {/* Info Panel */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        background: 'rgba(0,0,17,0.8)',
        border: '1px solid #0ff',
        padding: 20,
        maxWidth: 300,
        fontFamily: 'monospace'
      }}>
        <h1 style={{ fontSize: 18, marginBottom: 15, color: '#fff' }}>
          AIOS QUANTUM
        </h1>
        <div style={{ color: '#0ff', fontSize: 12 }}>
          <p>The Interface: Cube containing Sphere</p>
          <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '10px 0' }} />
          
          {heartbeatData ? (
            <>
              <p>Beat: <span style={{ color: '#0f0' }}>#{heartbeatData.beat_number || 0}</span></p>
              <p>Coherence: <span style={{ color: '#0f0' }}>{heartbeatData.coherence_estimate?.toFixed(4) || '—'}</span></p>
              <p>Entropy: <span style={{ color: '#0f0' }}>{heartbeatData.entropy?.toFixed(4) || '—'}</span></p>
              <p>Dominant: <span style={{ color: '#0f0' }}>|{heartbeatData.dominant_state || '?????'}⟩</span></p>
            </>
          ) : (
            <p>Loading heartbeat data...</p>
          )}
        </div>
      </div>

      {/* Controls */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        color: '#0ff',
        fontSize: 11,
        opacity: 0.7
      }}>
        Drag to rotate | Scroll to zoom | Space to animate
      </div>
      
      {/* Visualization Links */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        display: 'flex',
        gap: 10,
      }}>
        <Link href="/hypersphere/visualizations" style={{
          color: '#ff00ff',
          fontSize: 11,
          fontFamily: 'monospace',
          background: 'rgba(255,0,255,0.1)',
          padding: '8px 12px',
          borderRadius: 4,
          border: '1px solid #ff00ff',
          textDecoration: 'none',
        }}>
          🔮 Multi-Viz System
        </Link>
        <Link href="/hypersphere" style={{
          color: '#0ff',
          fontSize: 11,
          fontFamily: 'monospace',
          background: 'rgba(0,255,255,0.1)',
          padding: '8px 12px',
          borderRadius: 4,
          border: '1px solid #0ff',
          textDecoration: 'none',
        }}>
          🌐 Hypersphere
        </Link>
      </div>
    </main>
  )
}
