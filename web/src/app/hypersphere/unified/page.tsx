'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls, Line, Html, Points, PointMaterial } from '@react-three/drei'
import { Suspense, useState, useEffect, useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

// =============================================================================
// TYPES - UNIFIED SURFACE FORMAT
// =============================================================================

interface UnifiedVertex {
  id: string
  position: [number, number, number]
  color: [number, number, number, number]
  spherical: {
    theta: number
    phi: number
    depth: number
  }
  metadata: {
    class: string
    origin: string
    timestamp: string
    backend: string
    coherence: number
    entropy: number
    n_qubits: number
  }
  connections: string[]
}

interface UnifiedSurface {
  vertices: UnifiedVertex[]
  edges: Array<{
    from: string
    to: string
    from_pos?: [number, number, number]
    to_pos?: [number, number, number]
  }>
  statistics: {
    total: number
    by_class: Record<string, number>
    by_origin: Record<string, number>
  }
  generated_at: string
  version: string
  vertex_count: number
  edge_count: number
}

// =============================================================================
// EXPERIMENT CLASS COLORS
// =============================================================================

const CLASS_COLORS: Record<string, string> = {
  heartbeat: '#00ffff',      // Cyan
  cardiogram: '#0088ff',     // Blue
  arithmetic: '#00ff88',     // Green
  search: '#00ffaa',         // Teal
  factoring: '#88ff00',      // Yellow-green
  entanglement: '#ff00ff',   // Magenta
  teleportation: '#ff88ff',  // Pink
  simulation: '#8800ff',     // Purple
  pi_search: '#ff8800',      // Orange
  golden: '#ffcc00',         // Gold
  random: '#888888',         // Gray
  calibration: '#ffffff',    // White
  error: '#ff0000',          // Red
  witness: '#00ffcc',        // Cyan-green
}

const CLASS_ICONS: Record<string, string> = {
  heartbeat: '💓',
  cardiogram: '📊',
  arithmetic: '➕',
  search: '🔍',
  entanglement: '🔮',
  pi_search: 'π',
  golden: 'φ',
  random: '🎲',
}

// =============================================================================
// 3D COMPONENTS
// =============================================================================

function BosonicCube() {
  const h = 1.3
  const edges: Array<[[number, number, number], [number, number, number]]> = [
    [[-h, -h, -h], [h, -h, -h]], [[h, -h, -h], [h, h, -h]],
    [[h, h, -h], [-h, h, -h]], [[-h, h, -h], [-h, -h, -h]],
    [[-h, -h, h], [h, -h, h]], [[h, -h, h], [h, h, h]],
    [[h, h, h], [-h, h, h]], [[-h, h, h], [-h, -h, h]],
    [[-h, -h, -h], [-h, -h, h]], [[h, -h, -h], [h, -h, h]],
    [[h, h, -h], [h, h, h]], [[-h, h, -h], [-h, h, h]],
  ]
  
  return (
    <group>
      {edges.map((edge, i) => (
        <Line key={i} points={edge} color="#0066aa" lineWidth={1} transparent opacity={0.2} />
      ))}
    </group>
  )
}

// Reference sphere (ghost sphere showing ideal boundary)
function ReferenceSphere() {
  return (
    <mesh>
      <sphereGeometry args={[1.0, 32, 32]} />
      <meshBasicMaterial color="#003366" wireframe transparent opacity={0.08} />
    </mesh>
  )
}

// Experiment vertices as glowing points
function ExperimentVertices({ surfaceData, selectedClass }: { 
  surfaceData: UnifiedSurface
  selectedClass: string | null 
}) {
  const groupRef = useRef<THREE.Group>(null)
  
  const filteredVertices = useMemo(() => {
    if (!selectedClass) return surfaceData.vertices
    return surfaceData.vertices.filter(v => v.metadata.class === selectedClass)
  }, [surfaceData.vertices, selectedClass])
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05
    }
  })
  
  return (
    <group ref={groupRef}>
      {filteredVertices.map((vertex, i) => {
        const color = CLASS_COLORS[vertex.metadata.class] || '#ffffff'
        const scale = 0.8 + vertex.spherical.depth * 0.02
        const size = 0.03 + (1 - vertex.metadata.entropy / 5) * 0.03
        
        return (
          <mesh 
            key={vertex.id} 
            position={[
              vertex.position[0] * scale,
              vertex.position[1] * scale,
              vertex.position[2] * scale
            ]}
          >
            <sphereGeometry args={[size, 8, 8]} />
            <meshBasicMaterial 
              color={color} 
              transparent 
              opacity={0.9}
            />
          </mesh>
        )
      })}
    </group>
  )
}

// Connection lines between related experiments
function ExperimentConnections({ surfaceData }: { surfaceData: UnifiedSurface }) {
  const groupRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05
    }
  })
  
  const lines = useMemo(() => {
    const result: Array<{ points: [[number, number, number], [number, number, number]]; color: string }> = []
    
    // Create a lookup for vertices
    const vertexMap = new Map(surfaceData.vertices.map(v => [v.id, v]))
    
    // Build lines from edges
    for (const edge of surfaceData.edges) {
      const from = vertexMap.get(edge.from)
      const to = vertexMap.get(edge.to)
      
      if (from && to) {
        const fromPos = edge.from_pos || from.position
        const toPos = edge.to_pos || to.position
        
        result.push({
          points: [
            [fromPos[0] * 0.85, fromPos[1] * 0.85, fromPos[2] * 0.85],
            [toPos[0] * 0.85, toPos[1] * 0.85, toPos[2] * 0.85]
          ],
          color: CLASS_COLORS[from.metadata.class] || '#444444'
        })
      }
    }
    
    return result
  }, [surfaceData])
  
  if (lines.length === 0) return null
  
  return (
    <group ref={groupRef}>
      {lines.map((line, i) => (
        <Line 
          key={i} 
          points={line.points} 
          color={line.color} 
          lineWidth={1}
          transparent 
          opacity={0.3} 
        />
      ))}
    </group>
  )
}

// Topology regions (north pole = consciousness, equator = computation, south pole = constants)
function TopologyRegions() {
  return (
    <group>
      {/* North pole marker (Consciousness) */}
      <mesh position={[0, 0, 1.15]}>
        <ringGeometry args={[0.08, 0.1, 16]} />
        <meshBasicMaterial color="#00ffff" transparent opacity={0.5} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Equatorial band (Computation) */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.05, 0.01, 8, 64]} />
        <meshBasicMaterial color="#00ff88" transparent opacity={0.3} />
      </mesh>
      
      {/* South pole marker (Constants/Chaos) */}
      <mesh position={[0, 0, -1.15]}>
        <ringGeometry args={[0.08, 0.1, 16]} />
        <meshBasicMaterial color="#ff8800" transparent opacity={0.5} side={THREE.DoubleSide} />
      </mesh>
    </group>
  )
}

// Loading animation
function LoadingSphere() {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.5
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.3
    }
  })
  
  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[0.8, 1]} />
      <meshBasicMaterial color="#003366" wireframe />
    </mesh>
  )
}

// =============================================================================
// UI COMPONENTS
// =============================================================================

function StatsPanel({ 
  surfaceData, 
  selectedClass,
  onSelectClass
}: { 
  surfaceData: UnifiedSurface | null
  selectedClass: string | null
  onSelectClass: (cls: string | null) => void
}) {
  if (!surfaceData) return null
  
  const stats = surfaceData.statistics
  
  return (
    <div style={{
      position: 'absolute',
      top: 20,
      left: 20,
      background: 'rgba(0,0,20,0.92)',
      border: '1px solid #0ff',
      borderRadius: 6,
      padding: 20,
      maxWidth: 320,
      fontFamily: 'monospace',
      color: '#0ff',
      fontSize: 11,
      backdropFilter: 'blur(10px)'
    }}>
      <h1 style={{ fontSize: 16, marginBottom: 5, color: '#fff', letterSpacing: 2 }}>
        UNIFIED HYPERSPHERE
      </h1>
      <p style={{ marginBottom: 12, opacity: 0.6, fontSize: 10 }}>
        Quantum Experiment Topology v{surfaceData.version}
      </p>
      
      {/* Statistics */}
      <div style={{ marginBottom: 16 }}>
        <Row label="Total Experiments" value={stats.total} />
        <Row label="Vertices" value={surfaceData.vertex_count} />
        <Row label="Connections" value={surfaceData.edge_count} />
      </div>
      
      {/* Class Filter */}
      <div style={{ marginBottom: 12 }}>
        <p style={{ marginBottom: 8, fontSize: 10, opacity: 0.7 }}>EXPERIMENT CLASSES</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          <button
            onClick={() => onSelectClass(null)}
            style={{
              padding: '4px 8px',
              background: selectedClass === null ? '#0ff' : 'transparent',
              color: selectedClass === null ? '#000' : '#0ff',
              border: '1px solid #0ff',
              borderRadius: 3,
              cursor: 'pointer',
              fontSize: 9,
              fontFamily: 'monospace',
            }}
          >
            ALL
          </button>
          {Object.entries(stats.by_class).map(([cls, count]) => (
            <button
              key={cls}
              onClick={() => onSelectClass(cls === selectedClass ? null : cls)}
              style={{
                padding: '4px 8px',
                background: selectedClass === cls ? CLASS_COLORS[cls] : 'transparent',
                color: selectedClass === cls ? '#000' : CLASS_COLORS[cls] || '#0ff',
                border: `1px solid ${CLASS_COLORS[cls] || '#0ff'}`,
                borderRadius: 3,
                cursor: 'pointer',
                fontSize: 9,
                fontFamily: 'monospace',
              }}
            >
              {CLASS_ICONS[cls] || '•'} {cls} ({count})
            </button>
          ))}
        </div>
      </div>
      
      {/* Origin breakdown */}
      <div style={{ marginBottom: 12 }}>
        <p style={{ marginBottom: 4, fontSize: 10, opacity: 0.7 }}>ORIGIN</p>
        {Object.entries(stats.by_origin).map(([origin, count]) => (
          <Row 
            key={origin} 
            label={origin === 'ibm_quantum' ? '🔵 IBM Quantum' : '⚪ Simulator'} 
            value={count}
            color={origin === 'ibm_quantum' ? '#0088ff' : '#888888'}
          />
        ))}
      </div>
      
      {/* Topology Legend */}
      <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #0ff3' }}>
        <p style={{ marginBottom: 4, fontSize: 10, opacity: 0.7 }}>TOPOLOGY ZONES</p>
        <p style={{ fontSize: 9, marginBottom: 2 }}>
          <span style={{ color: '#00ffff' }}>● North</span> — Consciousness (heartbeats)
        </p>
        <p style={{ fontSize: 9, marginBottom: 2 }}>
          <span style={{ color: '#00ff88' }}>● Equator</span> — Computation (arithmetic)
        </p>
        <p style={{ fontSize: 9 }}>
          <span style={{ color: '#ff8800' }}>● South</span> — Constants (π, φ, random)
        </p>
      </div>
    </div>
  )
}

function Row({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <p style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
      <span style={{ opacity: 0.7 }}>{label}</span>
      <span style={{ color: color || '#0f0' }}>{value}</span>
    </p>
  )
}

// Tooltip showing experiment details on hover
function ExperimentTooltip({ surfaceData, selectedClass }: {
  surfaceData: UnifiedSurface
  selectedClass: string | null
}) {
  const [hovered, setHovered] = useState<UnifiedVertex | null>(null)
  
  // This would require raycasting - simplified for now
  return null
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function UnifiedHyperspherePage() {
  const [surfaceData, setSurfaceData] = useState<UnifiedSurface | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedClass, setSelectedClass] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    // Try to load unified surface from public data
    fetch('/data/unified_surface.json')
      .then(res => {
        if (!res.ok) throw new Error('Surface not found')
        return res.json()
      })
      .then(data => {
        setSurfaceData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load surface:', err)
        setError('Run scripts/build_unified_surface.py to generate surface data')
        setLoading(false)
      })
  }, [])
  
  return (
    <main style={{ height: '100vh', width: '100vw', background: '#000008' }}>
      <Canvas camera={{ position: [0, 1.5, 2.5], fov: 55 }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[5, 5, 5]} intensity={0.6} />
        <pointLight position={[-5, -5, -5]} intensity={0.3} color="#0066ff" />
        <pointLight position={[0, 5, 0]} intensity={0.2} color="#00ffff" />
        
        <BosonicCube />
        <ReferenceSphere />
        <TopologyRegions />
        
        <Suspense fallback={<LoadingSphere />}>
          {surfaceData && (
            <>
              <ExperimentVertices surfaceData={surfaceData} selectedClass={selectedClass} />
              <ExperimentConnections surfaceData={surfaceData} />
            </>
          )}
        </Suspense>
        
        <OrbitControls 
          enablePan={false} 
          minDistance={1.5} 
          maxDistance={6}
          autoRotate
          autoRotateSpeed={0.3}
          rotateSpeed={0.5}
        />
      </Canvas>
      
      {loading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#0ff',
          fontFamily: 'monospace',
          textAlign: 'center'
        }}>
          <p>Loading quantum experiments...</p>
        </div>
      )}
      
      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#ff6666',
          fontFamily: 'monospace',
          textAlign: 'center',
          background: 'rgba(0,0,0,0.8)',
          padding: 20,
          borderRadius: 8,
          border: '1px solid #ff6666'
        }}>
          <p style={{ marginBottom: 10 }}>⚠ {error}</p>
          <code style={{ fontSize: 10, opacity: 0.7 }}>
            python scripts/build_unified_surface.py
          </code>
        </div>
      )}
      
      <StatsPanel 
        surfaceData={surfaceData} 
        selectedClass={selectedClass}
        onSelectClass={setSelectedClass}
      />
      
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        color: '#0ff',
        fontSize: 10,
        opacity: 0.5,
        fontFamily: 'monospace'
      }}>
        Drag to rotate • Scroll to zoom • Click class to filter
      </div>
      
      <div style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        color: '#666',
        fontSize: 9,
        fontFamily: 'monospace'
      }}>
        Generated: {surfaceData?.generated_at?.split('T')[0] || '—'}
      </div>
    </main>
  )
}
