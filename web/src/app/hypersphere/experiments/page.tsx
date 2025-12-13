'use client'

// =============================================================================
// EXPERIMENT CLOUD - Visualization of ALL quantum experiments
// =============================================================================
// Uses compiled data from quantum_experiments.json
// =============================================================================

import { useRef, useMemo, useState, useEffect, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Html, Stars } from '@react-three/drei'
import * as THREE from 'three'
import { 
  CaptureControls, 
  CapturePanel,
  useScreenshotCapture,
  useVideoRecording 
} from '../visualizations/CaptureUtils'

// =============================================================================
// TYPES
// =============================================================================

interface ExperimentPoint {
  id: string
  type: string
  backend: string
  timestamp: string
  theta: number
  phi: number
  r: number
  hue: number
  saturation: number
  lightness: number
  size: number
  coherence: number
  fidelity: number
  entropy: number
}

interface ExperimentData {
  compiled_at: string
  total_experiments: number
  summary: {
    by_source: Record<string, number>
    by_type: Record<string, number>
    by_backend: Record<string, number>
    by_status: Record<string, number>
  }
  visualization_points: ExperimentPoint[]
}

// =============================================================================
// COLOR UTILITIES
// =============================================================================

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  let r, g, b
  if (s === 0) {
    r = g = b = l
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1/6) return p + (q - p) * 6 * t
      if (t < 1/2) return q
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
      return p
    }
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }
  return [r, g, b]
}

function sphericalToCartesian(theta: number, phi: number, r: number): [number, number, number] {
  return [
    r * Math.sin(theta) * Math.cos(phi),
    r * Math.cos(theta),
    r * Math.sin(theta) * Math.sin(phi)
  ]
}

// =============================================================================
// EXPERIMENT POINTS
// =============================================================================

function ExperimentPoints({ points, selectedType, hoveredId, onHover }: {
  points: ExperimentPoint[]
  selectedType: string | null
  hoveredId: string | null
  onHover: (id: string | null) => void
}) {
  const meshRef = useRef<THREE.InstancedMesh>(null!)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  
  // Filter points by selected type
  const filteredPoints = useMemo(() => {
    if (!selectedType) return points
    return points.filter(p => p.type === selectedType)
  }, [points, selectedType])
  
  // Update instance matrices and colors
  useEffect(() => {
    if (!meshRef.current) return
    
    const colorArray = new Float32Array(filteredPoints.length * 3)
    
    filteredPoints.forEach((point, i) => {
      // Position from spherical coords
      const [x, y, z] = sphericalToCartesian(point.theta, point.phi, point.r * 0.8)
      
      dummy.position.set(x, y, z)
      dummy.scale.setScalar(point.size * (hoveredId === point.id ? 2 : 1))
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
      
      // Color from HSL
      const [r, g, b] = hslToRgb(point.hue, point.saturation, point.lightness)
      colorArray[i * 3] = r
      colorArray[i * 3 + 1] = g
      colorArray[i * 3 + 2] = b
    })
    
    meshRef.current.instanceMatrix.needsUpdate = true
    meshRef.current.geometry.setAttribute(
      'color',
      new THREE.InstancedBufferAttribute(colorArray, 3)
    )
  }, [filteredPoints, hoveredId, dummy])
  
  // Animate
  useFrame((state) => {
    if (!meshRef.current) return
    
    const time = state.clock.elapsedTime
    
    filteredPoints.forEach((point, i) => {
      const [x, y, z] = sphericalToCartesian(point.theta, point.phi, point.r * 0.8)
      
      // Add subtle floating animation based on coherence
      const floatOffset = Math.sin(time * 2 + i * 0.5) * 0.01 * point.coherence
      
      dummy.position.set(x, y + floatOffset, z)
      dummy.scale.setScalar(point.size * (hoveredId === point.id ? 2 : 1))
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
    })
    
    meshRef.current.instanceMatrix.needsUpdate = true
  })
  
  return (
    <instancedMesh 
      ref={meshRef} 
      args={[undefined, undefined, filteredPoints.length]}
    >
      <sphereGeometry args={[1, 8, 8]} />
      <meshStandardMaterial 
        vertexColors 
        emissive="#ffffff"
        emissiveIntensity={0.3}
      />
    </instancedMesh>
  )
}

// =============================================================================
// REFERENCE SPHERE (Bosonic Container)
// =============================================================================

function ReferenceSphere() {
  return (
    <mesh>
      <sphereGeometry args={[0.78, 64, 64]} />
      <meshStandardMaterial
        color="#000011"
        transparent
        opacity={0.3}
        wireframe={false}
        side={THREE.BackSide}
      />
    </mesh>
  )
}

function WireframeSphere() {
  return (
    <mesh>
      <sphereGeometry args={[0.8, 32, 32]} />
      <meshBasicMaterial
        color="#001133"
        wireframe
        transparent
        opacity={0.2}
      />
    </mesh>
  )
}

// =============================================================================
// TOPOLOGY ZONES (North/Equator/South markers)
// =============================================================================

function TopologyZones() {
  const ringRef = useRef<THREE.Mesh>(null!)
  
  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.z = state.clock.elapsedTime * 0.1
    }
  })
  
  return (
    <group>
      {/* Equator ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.8, 0.003, 8, 64]} />
        <meshBasicMaterial color="#00ff88" transparent opacity={0.5} />
      </mesh>
      
      {/* North pole marker */}
      <mesh position={[0, 0.82, 0]}>
        <sphereGeometry args={[0.015, 16, 16]} />
        <meshBasicMaterial color="#00ffff" />
      </mesh>
      
      {/* South pole marker */}
      <mesh position={[0, -0.82, 0]}>
        <sphereGeometry args={[0.015, 16, 16]} />
        <meshBasicMaterial color="#ff00ff" />
      </mesh>
    </group>
  )
}

// =============================================================================
// STATS PANEL
// =============================================================================

function StatsPanel({ data, selectedType, onSelectType }: {
  data: ExperimentData | null
  selectedType: string | null
  onSelectType: (type: string | null) => void
}) {
  if (!data) return null
  
  const types = Object.entries(data.summary.by_type).sort((a, b) => b[1] - a[1])
  const backends = Object.entries(data.summary.by_backend).sort((a, b) => b[1] - a[1])
  
  return (
    <div style={{
      position: 'absolute',
      top: 20,
      left: 20,
      background: 'rgba(0, 0, 20, 0.9)',
      border: '1px solid #00ffff',
      borderRadius: 8,
      padding: 16,
      color: 'white',
      fontFamily: 'monospace',
      fontSize: 12,
      maxWidth: 280,
      zIndex: 100,
    }}>
      <h3 style={{ margin: '0 0 12px', color: '#00ffff' }}>
        🌐 QUANTUM EXPERIMENT CLOUD
      </h3>
      
      <div style={{ marginBottom: 12 }}>
        <strong>Total:</strong> {data.total_experiments} experiments
      </div>
      
      <div style={{ marginBottom: 12 }}>
        <strong>Compiled:</strong> {new Date(data.compiled_at).toLocaleString()}
      </div>
      
      <div style={{ marginBottom: 12 }}>
        <strong>By Type:</strong>
        <div style={{ marginTop: 4 }}>
          <button
            onClick={() => onSelectType(null)}
            style={{
              background: !selectedType ? '#00ffff' : '#001133',
              color: !selectedType ? '#000' : '#00ffff',
              border: '1px solid #00ffff',
              padding: '2px 8px',
              margin: '2px',
              borderRadius: 4,
              cursor: 'pointer',
              fontSize: 10,
            }}
          >
            ALL ({data.total_experiments})
          </button>
          {types.map(([type, count]) => (
            <button
              key={type}
              onClick={() => onSelectType(type === selectedType ? null : type)}
              style={{
                background: selectedType === type ? '#00ffff' : '#001133',
                color: selectedType === type ? '#000' : '#00ffff',
                border: '1px solid #00ffff',
                padding: '2px 8px',
                margin: '2px',
                borderRadius: 4,
                cursor: 'pointer',
                fontSize: 10,
              }}
            >
              {type} ({count})
            </button>
          ))}
        </div>
      </div>
      
      <div style={{ marginBottom: 8 }}>
        <strong>By Backend:</strong>
        <div style={{ marginTop: 4, fontSize: 10 }}>
          {backends.map(([backend, count]) => (
            <div key={backend} style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              padding: '2px 0',
              borderBottom: '1px solid #002244'
            }}>
              <span style={{ color: getBackendColor(backend) }}>{backend}</span>
              <span>{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function getBackendColor(backend: string): string {
  const colors: Record<string, string> = {
    'ibm_torino': '#00ffff',
    'ibm_fez': '#0088ff',
    'ibm_marrakesh': '#8800ff',
    'simulator': '#00ff88',
    'mock_simulator': '#888888',
    'unknown': '#ff0000',
  }
  return colors[backend] || '#ffffff'
}

// =============================================================================
// LEGEND
// =============================================================================

function Legend() {
  return (
    <div style={{
      position: 'absolute',
      bottom: 20,
      left: 20,
      background: 'rgba(0, 0, 20, 0.9)',
      border: '1px solid #00ffff',
      borderRadius: 8,
      padding: 12,
      color: 'white',
      fontFamily: 'monospace',
      fontSize: 10,
      zIndex: 100,
    }}>
      <div style={{ marginBottom: 8, fontWeight: 'bold' }}>TOPOLOGY ZONES</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{ color: '#00ffff' }}>●</span> North: Heartbeats
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{ color: '#00ff88' }}>○</span> Equator: Algorithms
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ color: '#ff00ff' }}>●</span> South: Exotic
      </div>
    </div>
  )
}

// =============================================================================
// MAIN SCENE
// =============================================================================

function Scene({ data, selectedType, onSelectType }: {
  data: ExperimentData | null
  selectedType: string | null
  onSelectType: (type: string | null) => void
}) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  
  if (!data) {
    return (
      <Html center>
        <div style={{ color: '#00ffff', fontFamily: 'monospace' }}>
          Loading quantum experiments...
        </div>
      </Html>
    )
  }
  
  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={0.5} />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#0088ff" />
      
      <Stars radius={100} depth={50} count={3000} factor={4} fade />
      
      <ReferenceSphere />
      <WireframeSphere />
      <TopologyZones />
      
      <ExperimentPoints 
        points={data.visualization_points}
        selectedType={selectedType}
        hoveredId={hoveredId}
        onHover={setHoveredId}
      />
      
      <OrbitControls 
        enableDamping 
        dampingFactor={0.05}
        minDistance={1}
        maxDistance={5}
      />
      
      <CaptureControls 
        mode="experiment-cloud"
        experimentCount={data?.total_experiments || 0}
      />
    </>
  )
}

// =============================================================================
// CAPTURE BUTTON WRAPPER (inside Canvas for capture functionality)
// =============================================================================

function CaptureButtonsInCanvas({ 
  onCaptureReady 
}: { 
  onCaptureReady: (fns: { screenshot: () => void; toggleRecord: () => void; isRecording: boolean; duration: number }) => void 
}) {
  const { downloadScreenshot } = useScreenshotCapture()
  const { isRecording, recordingDuration, startRecording, downloadRecording } = useVideoRecording()
  
  const handleScreenshot = useCallback(() => {
    downloadScreenshot({ mode: 'experiment-cloud' })
  }, [downloadScreenshot])
  
  const handleToggleRecord = useCallback(() => {
    if (isRecording) {
      downloadRecording()
    } else {
      startRecording({ fps: 30 })
    }
  }, [isRecording, startRecording, downloadRecording])
  
  useEffect(() => {
    onCaptureReady({
      screenshot: handleScreenshot,
      toggleRecord: handleToggleRecord,
      isRecording,
      duration: recordingDuration
    })
  }, [handleScreenshot, handleToggleRecord, isRecording, recordingDuration, onCaptureReady])
  
  return null
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ExperimentCloudPage() {
  const [data, setData] = useState<ExperimentData | null>(null)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [captureState, setCaptureState] = useState<{
    screenshot: () => void
    toggleRecord: () => void
    isRecording: boolean
    duration: number
  } | null>(null)
  
  // Load experiment data
  useEffect(() => {
    fetch('/quantum_experiments.json')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setData)
      .catch(err => {
        console.error('Failed to load experiments:', err)
        setError(err.message)
      })
  }, [])
  
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#000011' }}>
      <Canvas camera={{ position: [0, 0, 2.5], fov: 60 }}>
        <Scene 
          data={data} 
          selectedType={selectedType}
          onSelectType={setSelectedType}
        />
        <CaptureButtonsInCanvas onCaptureReady={setCaptureState} />
      </Canvas>
      
      <StatsPanel 
        data={data}
        selectedType={selectedType}
        onSelectType={setSelectedType}
      />
      
      <Legend />
      
      {/* Capture Controls */}
      {captureState && (
        <CapturePanel
          isRecording={captureState.isRecording}
          recordingDuration={captureState.duration}
          onScreenshot={captureState.screenshot}
          onRecordToggle={captureState.toggleRecord}
        />
      )}
      
      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(255, 0, 0, 0.9)',
          padding: 20,
          borderRadius: 8,
          color: 'white',
          fontFamily: 'monospace',
        }}>
          Error: {error}
        </div>
      )}
      
      <div style={{
        position: 'absolute',
        top: 20,
        right: 20,
        color: '#00ffff',
        fontFamily: 'monospace',
        fontSize: 10,
        textAlign: 'right',
      }}>
        <div>AIOS QUANTUM</div>
        <div>Experiment Cloud v1.0</div>
      </div>
    </div>
  )
}
