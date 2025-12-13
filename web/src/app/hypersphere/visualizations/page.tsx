'use client'

// =============================================================================
// QUANTUM VISUALIZATION - MODULAR SHELL
// =============================================================================
// Multi-modal visualization application supporting different quantum data views
// Switch between: Topology Mesh, Hypergate Sphere, and future modes
// =============================================================================

import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Suspense, useState, useEffect, useCallback, useRef } from 'react'
import Link from 'next/link'

// Type imports
import { 
  VisualizationMode, 
  VISUALIZATION_MODES, 
  HypersphereSurfaceData, 
  UnifiedSurface,
  DEFAULT_CONTROLS
} from './types'

// Visualization components
import { 
  DisplacedSphere, 
  MeasuredVertices, 
  BosonicCube as TopologyBosonicCube,
  TopologyStatsPanel 
} from './TopologyMesh'

import {
  BosonicCube as HypergateBosonicCube,
  ReferenceSphere,
  TopologyRegions,
  ExperimentVertices,
  ExperimentConnections,
  HypergateStatsPanel
} from './HypergateSphere'

// =============================================================================
// CAPTURE COMPONENT (inside Canvas)
// =============================================================================

function CaptureController({ 
  onCaptureReady 
}: { 
  onCaptureReady: (capture: { screenshot: () => void, startRecording: () => void, stopRecording: () => Promise<void> }) => void 
}) {
  const { gl, scene, camera } = useThree()
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  
  const screenshot = useCallback(() => {
    gl.render(scene, camera)
    const dataUrl = gl.domElement.toDataURL('image/png', 1.0)
    const now = new Date()
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19)
    const filename = `aios-quantum_${timestamp}.png`
    
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    console.log('📸 Screenshot saved:', filename)
  }, [gl, scene, camera])
  
  const startRecording = useCallback(() => {
    const canvas = gl.domElement
    const stream = canvas.captureStream(30)
    
    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
      ? 'video/webm;codecs=vp9'
      : 'video/webm'
    
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 5000000
    })
    
    chunksRef.current = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data)
      }
    }
    
    mediaRecorder.start(100)
    mediaRecorderRef.current = mediaRecorder
    console.log('🎬 Recording started')
  }, [gl])
  
  const stopRecording = useCallback(async () => {
    return new Promise<void>((resolve) => {
      const mediaRecorder = mediaRecorderRef.current
      if (!mediaRecorder) {
        resolve()
        return
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        const now = new Date()
        const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19)
        const filename = `aios-quantum_recording_${timestamp}.webm`
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        console.log('🎬 Recording saved:', filename, `(${(blob.size / 1024 / 1024).toFixed(2)} MB)`)
        mediaRecorderRef.current = null
        resolve()
      }
      
      mediaRecorder.stop()
    })
  }, [])
  
  useEffect(() => {
    onCaptureReady({ screenshot, startRecording, stopRecording })
  }, [screenshot, startRecording, stopRecording, onCaptureReady])
  
  return null
}

// =============================================================================
// LOADING COMPONENTS
// =============================================================================

function LoadingSphere({ mode }: { mode: VisualizationMode }) {
  const config = VISUALIZATION_MODES.find(m => m.id === mode)
  const color = config?.color || '#00ffff'
  
  return (
    <mesh>
      <icosahedronGeometry args={[0.8, 1]} />
      <meshBasicMaterial color={color} wireframe opacity={0.5} transparent />
    </mesh>
  )
}

// =============================================================================
// MODE SWITCHER UI
// =============================================================================

function ModeSwitcher({ 
  currentMode, 
  onModeChange 
}: { 
  currentMode: VisualizationMode
  onModeChange: (mode: VisualizationMode) => void 
}) {
  const [expanded, setExpanded] = useState(false)
  const availableModes = VISUALIZATION_MODES.filter(m => m.available)
  const currentConfig = VISUALIZATION_MODES.find(m => m.id === currentMode)
  
  return (
    <div style={{
      position: 'absolute',
      top: 20,
      right: 20,
      fontFamily: 'monospace',
      fontSize: 11,
      zIndex: 100,
    }}>
      {/* Current mode button */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 14px',
          background: 'rgba(0,0,20,0.95)',
          border: `1px solid ${currentConfig?.color || '#0ff'}`,
          borderRadius: expanded ? '6px 6px 0 0' : 6,
          cursor: 'pointer',
          color: currentConfig?.color || '#0ff',
          fontFamily: 'monospace',
          fontSize: 11,
          minWidth: 180,
          textAlign: 'left',
        }}
      >
        <span style={{ fontSize: 16 }}>{currentConfig?.icon}</span>
        <span style={{ flex: 1 }}>{currentConfig?.name}</span>
        <span style={{ 
          transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s'
        }}>▼</span>
      </button>
      
      {/* Dropdown */}
      {expanded && (
        <div style={{
          background: 'rgba(0,0,20,0.95)',
          border: `1px solid ${currentConfig?.color || '#0ff'}`,
          borderTop: 'none',
          borderRadius: '0 0 6px 6px',
          overflow: 'hidden',
        }}>
          {availableModes.map(mode => (
            <button
              key={mode.id}
              onClick={() => {
                onModeChange(mode.id)
                setExpanded(false)
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                width: '100%',
                padding: '10px 14px',
                background: mode.id === currentMode 
                  ? `${mode.color}22`
                  : 'transparent',
                border: 'none',
                borderBottom: '1px solid #ffffff11',
                cursor: 'pointer',
                color: mode.color,
                fontFamily: 'monospace',
                fontSize: 11,
                textAlign: 'left',
                transition: 'background 0.2s',
              }}
              onMouseEnter={(e) => {
                if (mode.id !== currentMode) {
                  e.currentTarget.style.background = `${mode.color}11`
                }
              }}
              onMouseLeave={(e) => {
                if (mode.id !== currentMode) {
                  e.currentTarget.style.background = 'transparent'
                }
              }}
            >
              <span style={{ fontSize: 14 }}>{mode.icon}</span>
              <div style={{ flex: 1 }}>
                <div>{mode.name}</div>
                <div style={{ fontSize: 8, opacity: 0.6, marginTop: 2 }}>
                  {mode.description.slice(0, 50)}...
                </div>
              </div>
            </button>
          ))}
          
          {/* Coming Soon section */}
          <div style={{ 
            padding: '8px 14px', 
            borderTop: '1px solid #ffffff22',
            opacity: 0.4 
          }}>
            <div style={{ fontSize: 9, marginBottom: 6, color: '#888' }}>COMING SOON</div>
            {VISUALIZATION_MODES.filter(m => !m.available).map(mode => (
              <div 
                key={mode.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 0',
                  color: '#555',
                  fontSize: 9,
                }}
              >
                <span>{mode.icon}</span>
                <span>{mode.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// TOPOLOGY MESH SCENE
// =============================================================================

function TopologyMeshScene({ 
  surfaceData,
  wireframe 
}: { 
  surfaceData: HypersphereSurfaceData | null
  wireframe: boolean
}) {
  if (!surfaceData) return null
  
  return (
    <>
      <TopologyBosonicCube />
      <DisplacedSphere surfaceData={surfaceData} wireframe={wireframe} />
      <MeasuredVertices surfaceData={surfaceData} />
    </>
  )
}

// =============================================================================
// HYPERGATE SPHERE SCENE
// =============================================================================

function HypergateSphereScene({ 
  surfaceData,
  selectedClass 
}: { 
  surfaceData: UnifiedSurface | null
  selectedClass: string | null
}) {
  if (!surfaceData) return null
  
  return (
    <>
      <HypergateBosonicCube />
      <ReferenceSphere />
      <TopologyRegions />
      <ExperimentVertices surfaceData={surfaceData} selectedClass={selectedClass} />
      <ExperimentConnections surfaceData={surfaceData} />
    </>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function QuantumVisualization() {
  // Mode state
  const [mode, setMode] = useState<VisualizationMode>('topology')
  
  // Data state
  const [topologyData, setTopologyData] = useState<HypersphereSurfaceData | null>(null)
  const [unifiedData, setUnifiedData] = useState<UnifiedSurface | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Control state
  const [wireframe, setWireframe] = useState(false)
  const [selectedClass, setSelectedClass] = useState<string | null>(null)
  
  // Capture state
  const [captureApi, setCaptureApi] = useState<{
    screenshot: () => void
    startRecording: () => void
    stopRecording: () => Promise<void>
  } | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null)
  
  // Get current mode config
  const currentConfig = VISUALIZATION_MODES.find(m => m.id === mode)!
  
  // Load data based on mode
  useEffect(() => {
    setLoading(true)
    setError(null)
    
    if (mode === 'topology') {
      // Load topology surface data
      fetch('/api/surface/latest')
        .then(res => res.ok ? res.json() : Promise.reject())
        .then(data => {
          setTopologyData(data)
          setLoading(false)
        })
        .catch(() => {
          // Use sample data
          setTopologyData(SAMPLE_TOPOLOGY_DATA)
          setLoading(false)
        })
    } else if (mode === 'unified') {
      // Load unified surface data
      fetch('/data/unified_surface.json')
        .then(res => {
          if (!res.ok) throw new Error('Surface not found')
          return res.json()
        })
        .then(data => {
          setUnifiedData(data)
          setLoading(false)
        })
        .catch(err => {
          console.error('Failed to load unified surface:', err)
          setError('Run scripts/build_unified_surface.py to generate unified surface')
          setLoading(false)
        })
    }
  }, [mode])
  
  // Recording handlers
  const handleScreenshot = useCallback(() => {
    if (captureApi) {
      captureApi.screenshot()
    }
  }, [captureApi])
  
  const handleRecordToggle = useCallback(async () => {
    if (!captureApi) return
    
    if (isRecording) {
      // Stop recording
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current)
        recordingTimerRef.current = null
      }
      setIsRecording(false)
      await captureApi.stopRecording()
      setRecordingDuration(0)
    } else {
      // Start recording
      captureApi.startRecording()
      setIsRecording(true)
      setRecordingDuration(0)
      recordingTimerRef.current = setInterval(() => {
        setRecordingDuration(d => d + 1)
      }, 1000)
    }
  }, [captureApi, isRecording])
  
  // Format recording duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  // Camera position based on mode
  const cameraPosition: [number, number, number] = mode === 'topology' 
    ? [0, 0, 2.8] 
    : [0, 1.5, 2.5]
  
  return (
    <main style={{ 
      height: '100vh', 
      width: '100vw', 
      background: mode === 'topology' ? '#000010' : '#000008' 
    }}>
      <Canvas camera={{ position: cameraPosition, fov: 55 }}>
        <ambientLight intensity={mode === 'topology' ? 0.5 : 0.4} />
        <pointLight position={[5, 5, 5]} intensity={mode === 'topology' ? 0.7 : 0.6} />
        <pointLight position={[-5, -5, -5]} intensity={0.3} color="#0066ff" />
        {mode === 'unified' && (
          <pointLight position={[0, 5, 0]} intensity={0.2} color="#00ffff" />
        )}
        
        <Suspense fallback={<LoadingSphere mode={mode} />}>
          {mode === 'topology' && (
            <TopologyMeshScene surfaceData={topologyData} wireframe={wireframe} />
          )}
          {mode === 'unified' && (
            <HypergateSphereScene surfaceData={unifiedData} selectedClass={selectedClass} />
          )}
        </Suspense>
        
        <CaptureController onCaptureReady={setCaptureApi} />
        
        <OrbitControls 
          enablePan={false} 
          minDistance={1.5} 
          maxDistance={6}
          autoRotate={mode === 'unified'}
          autoRotateSpeed={0.3}
          rotateSpeed={0.5}
        />
      </Canvas>
      
      {/* Loading overlay */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: currentConfig.color,
          fontFamily: 'monospace',
          textAlign: 'center'
        }}>
          <p>Loading {currentConfig.name}...</p>
        </div>
      )}
      
      {/* Error overlay */}
      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#ff6666',
          fontFamily: 'monospace',
          textAlign: 'center',
          background: 'rgba(0,0,0,0.9)',
          padding: 24,
          borderRadius: 8,
          border: '1px solid #ff6666',
          maxWidth: 400,
        }}>
          <p style={{ marginBottom: 12 }}>⚠ {error}</p>
          <code style={{ fontSize: 10, opacity: 0.7, display: 'block' }}>
            python scripts/build_unified_surface.py
          </code>
        </div>
      )}
      
      {/* Mode Switcher */}
      <ModeSwitcher currentMode={mode} onModeChange={setMode} />
      
      {/* Header */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        fontFamily: 'monospace',
      }}>
        <h1 style={{ 
          fontSize: 18, 
          marginBottom: 4, 
          color: '#fff', 
          letterSpacing: 2,
          textShadow: `0 0 20px ${currentConfig.color}44`
        }}>
          AIOS QUANTUM
        </h1>
        <p style={{ 
          fontSize: 10, 
          color: currentConfig.color, 
          opacity: 0.7 
        }}>
          Multi-Modal Visualization System
        </p>
      </div>
      
      {/* Mode-specific stats panel */}
      <div style={{
        position: 'absolute',
        top: 90,
        left: 20,
        maxWidth: 280,
      }}>
        {mode === 'topology' && (
          <TopologyStatsPanel 
            surfaceData={topologyData}
            wireframe={wireframe}
            onWireframeChange={setWireframe}
          />
        )}
        {mode === 'unified' && (
          <HypergateStatsPanel 
            surfaceData={unifiedData}
            selectedClass={selectedClass}
            onSelectClass={setSelectedClass}
          />
        )}
      </div>
      
      {/* Footer */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        color: currentConfig.color,
        fontSize: 10,
        opacity: 0.5,
        fontFamily: 'monospace'
      }}>
        Drag to rotate • Scroll to zoom
        {mode === 'unified' && ' • Click class to filter'}
      </div>
      
      {/* Capture Controls */}
      <div style={{
        position: 'absolute',
        bottom: 60,
        right: 20,
        display: 'flex',
        gap: 8,
        fontFamily: 'monospace',
        fontSize: 10,
      }}>
        <button
          onClick={handleScreenshot}
          disabled={!captureApi}
          style={{
            padding: '8px 12px',
            background: 'rgba(0,255,136,0.15)',
            color: '#00ff88',
            border: '1px solid #00ff88',
            borderRadius: 4,
            cursor: captureApi ? 'pointer' : 'not-allowed',
            fontFamily: 'monospace',
            fontSize: 10,
            opacity: captureApi ? 1 : 0.5,
          }}
          title="Save PNG screenshot"
        >
          📸 Snapshot
        </button>
        
        <button
          onClick={handleRecordToggle}
          disabled={!captureApi}
          style={{
            padding: '8px 12px',
            background: isRecording ? 'rgba(255,0,0,0.2)' : 'rgba(255,136,0,0.15)',
            color: isRecording ? '#ff4444' : '#ff8800',
            border: `1px solid ${isRecording ? '#ff4444' : '#ff8800'}`,
            borderRadius: 4,
            cursor: captureApi ? 'pointer' : 'not-allowed',
            fontFamily: 'monospace',
            fontSize: 10,
            minWidth: 90,
            opacity: captureApi ? 1 : 0.5,
          }}
          title={isRecording ? 'Stop & save WebM video' : 'Start recording'}
        >
          {isRecording ? (
            <>⏹ {formatDuration(recordingDuration)}</>
          ) : (
            <>🎬 Record</>
          )}
        </button>
      </div>
      
      {/* Back link */}
      <Link href="/" style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        color: currentConfig.color,
        fontSize: 10,
        fontFamily: 'monospace',
        background: `${currentConfig.color}11`,
        padding: '6px 10px',
        borderRadius: 4,
        border: `1px solid ${currentConfig.color}44`,
        textDecoration: 'none',
        opacity: 0.7,
      }}>
        ← Back to Home
      </Link>
    </main>
  )
}

// =============================================================================
// SAMPLE DATA (fallback for topology mode)
// =============================================================================

const SAMPLE_TOPOLOGY_DATA: HypersphereSurfaceData = {
  type: "hypersphere_surface",
  vertex_count: 20,
  total_beats: 4,
  heights: [-1.0, -0.668, -0.980, -0.688, -0.980, -0.961, -0.824, -0.961, -0.668, -0.961, -0.980, -0.668, -0.980, -0.570, -1.0, 0.016, -0.590, 0.426, -0.844, -0.043],
  vertices: [
    { spherical: { theta: 0.524, phi: 0 }, cartesian: { x: 0.45, y: 0, z: 0.779 }, height: -1.0, uv: { u: 0, v: 0.167 }, quantum: { beat: 0, error: 0 } },
    { spherical: { theta: 1.047, phi: 0 }, cartesian: { x: 0.808, y: 0, z: 0.467 }, height: -0.668, uv: { u: 0, v: 0.333 }, quantum: { beat: 0, error: 0.0166 } },
    { spherical: { theta: 1.571, phi: 0 }, cartesian: { x: 0.902, y: 0, z: 0 }, height: -0.980, uv: { u: 0, v: 0.5 }, quantum: { beat: 0, error: 0.001 } },
    { spherical: { theta: 2.094, phi: 0 }, cartesian: { x: 0.806, y: 0, z: -0.466 }, height: -0.688, uv: { u: 0, v: 0.667 }, quantum: { beat: 0, error: 0.0156 } },
    { spherical: { theta: 2.618, phi: 0 }, cartesian: { x: 0.451, y: 0, z: -0.781 }, height: -0.980, uv: { u: 0, v: 0.833 }, quantum: { beat: 0, error: 0.001 } },
    { spherical: { theta: 0.524, phi: 1.571 }, cartesian: { x: 0, y: 0.452, z: 0.783 }, height: -0.961, uv: { u: 0.25, v: 0.167 }, quantum: { beat: 1, error: 0.00195 } },
    { spherical: { theta: 1.047, phi: 1.571 }, cartesian: { x: 0, y: 0.795, z: 0.459 }, height: -0.824, uv: { u: 0.25, v: 0.333 }, quantum: { beat: 1, error: 0.00879 } },
    { spherical: { theta: 1.571, phi: 1.571 }, cartesian: { x: 0, y: 0.904, z: 0 }, height: -0.961, uv: { u: 0.25, v: 0.5 }, quantum: { beat: 1, error: 0.00195 } },
    { spherical: { theta: 2.094, phi: 1.571 }, cartesian: { x: 0, y: 0.808, z: -0.467 }, height: -0.668, uv: { u: 0.25, v: 0.667 }, quantum: { beat: 1, error: 0.0166 } },
    { spherical: { theta: 2.618, phi: 1.571 }, cartesian: { x: 0, y: 0.452, z: -0.783 }, height: -0.961, uv: { u: 0.25, v: 0.833 }, quantum: { beat: 1, error: 0.00195 } },
    { spherical: { theta: 0.524, phi: 3.142 }, cartesian: { x: -0.451, y: 0, z: 0.781 }, height: -0.980, uv: { u: 0.5, v: 0.167 }, quantum: { beat: 2, error: 0.001 } },
    { spherical: { theta: 1.047, phi: 3.142 }, cartesian: { x: -0.808, y: 0, z: 0.467 }, height: -0.668, uv: { u: 0.5, v: 0.333 }, quantum: { beat: 2, error: 0.0166 } },
    { spherical: { theta: 1.571, phi: 3.142 }, cartesian: { x: -0.902, y: 0, z: 0 }, height: -0.980, uv: { u: 0.5, v: 0.5 }, quantum: { beat: 2, error: 0.001 } },
    { spherical: { theta: 2.094, phi: 3.142 }, cartesian: { x: -0.817, y: 0, z: -0.471 }, height: -0.570, uv: { u: 0.5, v: 0.667 }, quantum: { beat: 2, error: 0.0215 } },
    { spherical: { theta: 2.618, phi: 3.142 }, cartesian: { x: -0.45, y: 0, z: -0.779 }, height: -1.0, uv: { u: 0.5, v: 0.833 }, quantum: { beat: 2, error: 0 } },
    { spherical: { theta: 0.524, phi: 4.712 }, cartesian: { x: 0, y: -0.501, z: 0.867 }, height: 0.016, uv: { u: 0.75, v: 0.167 }, quantum: { beat: 3, error: 0.0508 } },
    { spherical: { theta: 1.047, phi: 4.712 }, cartesian: { x: 0, y: -0.815, z: 0.471 }, height: -0.590, uv: { u: 0.75, v: 0.333 }, quantum: { beat: 3, error: 0.0205 } },
    { spherical: { theta: 1.571, phi: 4.712 }, cartesian: { x: 0, y: -1.043, z: 0 }, height: 0.426, uv: { u: 0.75, v: 0.5 }, quantum: { beat: 3, error: 0.0713 } },
    { spherical: { theta: 2.094, phi: 4.712 }, cartesian: { x: 0, y: -0.793, z: -0.458 }, height: -0.844, uv: { u: 0.75, v: 0.667 }, quantum: { beat: 3, error: 0.00781 } },
    { spherical: { theta: 2.618, phi: 4.712 }, cartesian: { x: 0, y: -0.498, z: -0.862 }, height: -0.043, uv: { u: 0.75, v: 0.833 }, quantum: { beat: 3, error: 0.0479 } },
  ],
  statistics: {
    mean_height: -0.696,
    height_variance: 0.149,
    mean_error: 0.0152,
    max_error: 0.0713,
    min_error: 0
  },
  source_data: [
    { beat: 0, backend: "ibm_fez", type: "cardiogram", timestamp: "2025-12-12T19:48:22" },
    { beat: 1, backend: "ibm_fez", type: "cardiogram", timestamp: "2025-12-12T19:56:42" },
    { beat: 2, backend: "ibm_fez", type: "cardiogram", timestamp: "2025-12-12T19:57:36" },
    { beat: 3, backend: "ibm_torino", type: "heartbeat", timestamp: "2025-12-11T23:27:52" }
  ]
}
