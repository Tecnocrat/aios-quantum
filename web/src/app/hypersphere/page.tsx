'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls, Line, Html } from '@react-three/drei'
import { Suspense, useState, useEffect, useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import Link from 'next/link'

// =============================================================================
// TYPES
// =============================================================================

interface SurfaceVertex {
  spherical: { theta: number; phi: number }
  cartesian: { x: number; y: number; z: number }
  height: number
  uv: { u: number; v: number }
  quantum: {
    beat: number
    error: number
  }
}

interface HypersphereSurfaceData {
  type: string
  vertex_count: number
  total_beats: number
  heights: number[]
  vertices: SurfaceVertex[]
  statistics: {
    mean_height: number
    height_variance: number
    mean_error: number
    max_error: number
    min_error: number
  }
  source_data?: Array<{
    beat: number
    backend: string
    type: string
    timestamp: string
  }>
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function heightToColor(height: number): THREE.Color {
  const t = (height + 1) / 2
  
  if (t < 0.4) {
    const s = t / 0.4
    return new THREE.Color().setHSL(0.55 + 0.1 * s, 0.9, 0.3 + 0.3 * s)
  } else if (t < 0.6) {
    const s = (t - 0.4) / 0.2
    return new THREE.Color().setHSL(0.55, 0.3, 0.7)
  } else {
    const s = (t - 0.6) / 0.4
    return new THREE.Color().setHSL(0.08 - 0.08 * s, 0.9, 0.5 + 0.15 * s)
  }
}

// =============================================================================
// 3D COMPONENTS
// =============================================================================

function BosonicCube() {
  const h = 1.1
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
        <Line key={i} points={edge} color="#00ffff" lineWidth={1} transparent opacity={0.25} />
      ))}
    </group>
  )
}

// The quantum-displaced sphere mesh
function DisplacedSphere({ surfaceData, wireframe }: { surfaceData: HypersphereSurfaceData; wireframe: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const resolution = 48
  const baseRadius = 0.85
  
  const geometry = useMemo(() => {
    const vertices = surfaceData.vertices
    const positions: number[] = []
    const colors: number[] = []
    const indices: number[] = []
    
    // Generate sphere grid with interpolated heights
    for (let i = 0; i <= resolution; i++) {
      const theta = (i / resolution) * Math.PI
      
      for (let j = 0; j <= resolution; j++) {
        const phi = (j / resolution) * 2 * Math.PI
        
        // Interpolate height from measured vertices
        let height = 0
        let totalWeight = 0
        
        for (const v of vertices) {
          const dTheta = Math.abs(v.spherical.theta - theta)
          const dPhi = Math.min(
            Math.abs(v.spherical.phi - phi),
            2 * Math.PI - Math.abs(v.spherical.phi - phi)
          )
          const dist = Math.sqrt(dTheta * dTheta + dPhi * dPhi)
          
          if (dist < 0.01) {
            height = v.height
            totalWeight = 1
            break
          } else if (dist < Math.PI * 0.6) {
            const weight = 1 / (dist * dist + 0.05)
            height += v.height * weight
            totalWeight += weight
          }
        }
        
        if (totalWeight > 0) height /= totalWeight
        
        // Position with displacement
        const displacement = height * 0.12
        const r = baseRadius + displacement
        
        positions.push(
          r * Math.sin(theta) * Math.cos(phi),
          r * Math.sin(theta) * Math.sin(phi),
          r * Math.cos(theta)
        )
        
        const color = heightToColor(height)
        colors.push(color.r, color.g, color.b)
      }
    }
    
    // Generate triangle indices
    for (let i = 0; i < resolution; i++) {
      for (let j = 0; j < resolution; j++) {
        const a = i * (resolution + 1) + j
        const b = a + resolution + 1
        indices.push(a, b, a + 1, b, b + 1, a + 1)
      }
    }
    
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
    geo.setIndex(indices)
    geo.computeVertexNormals()
    
    return geo
  }, [surfaceData])
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.08
    }
  })
  
  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial 
        vertexColors 
        wireframe={wireframe} 
        side={THREE.DoubleSide}
        metalness={0.2}
        roughness={0.8}
      />
    </mesh>
  )
}

// Measured vertex points (the actual quantum data)
function MeasuredVertices({ surfaceData }: { surfaceData: HypersphereSurfaceData }) {
  const pointsRef = useRef<THREE.Points>(null)
  
  const { positions, colors, sizes } = useMemo(() => {
    const pos: number[] = []
    const col: number[] = []
    const siz: number[] = []
    
    for (const v of surfaceData.vertices) {
      // Slightly expand to be visible above mesh
      const scale = 1.02
      pos.push(v.cartesian.x * scale, v.cartesian.y * scale, v.cartesian.z * scale)
      
      const color = heightToColor(v.height)
      col.push(color.r, color.g, color.b)
      
      // Larger points for higher error
      siz.push(0.04 + Math.abs(v.height) * 0.06)
    }
    
    return {
      positions: new Float32Array(pos),
      colors: new Float32Array(col),
      sizes: new Float32Array(siz)
    }
  }, [surfaceData])
  
  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.08
    }
  })
  
  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={colors.length / 3} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} vertexColors transparent opacity={0.95} sizeAttenuation />
    </points>
  )
}

// Loading placeholder
function LoadingSphere() {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.5
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
  viewMode, 
  onViewModeChange 
}: { 
  surfaceData: HypersphereSurfaceData | null
  viewMode: string
  onViewModeChange: (mode: string) => void 
}) {
  return (
    <div style={{
      position: 'absolute',
      top: 20,
      left: 20,
      background: 'rgba(0,0,20,0.92)',
      border: '1px solid #0ff',
      borderRadius: 6,
      padding: 20,
      maxWidth: 300,
      fontFamily: 'monospace',
      color: '#0ff',
      fontSize: 11,
      backdropFilter: 'blur(10px)'
    }}>
      <h1 style={{ fontSize: 16, marginBottom: 5, color: '#fff', letterSpacing: 2 }}>
        AIOS QUANTUM
      </h1>
      <p style={{ marginBottom: 12, opacity: 0.6, fontSize: 10 }}>Hypersphere Topology</p>
      
      {surfaceData && (
        <>
          <div style={{ marginBottom: 12 }}>
            <Row label="Vertices" value={surfaceData.vertex_count} />
            <Row label="Beats" value={surfaceData.total_beats} />
            <Row label="Mean Error" value={`${(surfaceData.statistics.mean_error * 100).toFixed(2)}%`} />
            <Row label="Max Error" value={`${(surfaceData.statistics.max_error * 100).toFixed(2)}%`} color="#ff6666" />
            <Row label="Roughness" value={surfaceData.statistics.height_variance.toFixed(4)} />
          </div>
          
          {/* Color Legend */}
          <div style={{ marginBottom: 12 }}>
            <p style={{ marginBottom: 4, fontSize: 10, opacity: 0.7 }}>Height (Error → Topology)</p>
            <div style={{ 
              height: 8,
              background: 'linear-gradient(to right, #0088cc, #888888, #ff6633)',
              borderRadius: 2
            }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, marginTop: 2, opacity: 0.6 }}>
              <span>▼ Valley (0%)</span>
              <span>Mountain ▲ (7%+)</span>
            </div>
          </div>
          
          {/* Source Info */}
          {surfaceData.source_data && (
            <div style={{ marginBottom: 12 }}>
              <p style={{ marginBottom: 4, fontSize: 10, opacity: 0.7 }}>Source Backends</p>
              {surfaceData.source_data.slice(0, 4).map((src, i) => (
                <p key={i} style={{ fontSize: 9, opacity: 0.8 }}>
                  <span style={{ color: '#ff0' }}>{src.backend}</span> • Beat {src.beat}
                </p>
              ))}
            </div>
          )}
        </>
      )}
      
      {/* View Mode */}
      <div style={{ display: 'flex', gap: 4 }}>
        {['solid', 'wireframe'].map(mode => (
          <button
            key={mode}
            onClick={() => onViewModeChange(mode)}
            style={{
              flex: 1,
              padding: '6px 8px',
              background: viewMode === mode ? '#0ff' : 'transparent',
              color: viewMode === mode ? '#000' : '#0ff',
              border: '1px solid #0ff',
              borderRadius: 3,
              cursor: 'pointer',
              fontSize: 9,
              fontFamily: 'monospace',
              textTransform: 'uppercase'
            }}
          >
            {mode}
          </button>
        ))}
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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function HyperspherePage() {
  const [surfaceData, setSurfaceData] = useState<HypersphereSurfaceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState('solid')
  
  useEffect(() => {
    // Try API first, then fallback to sample
    fetch('/api/surface/latest')
      .then(res => res.ok ? res.json() : Promise.reject())
      .then(data => { setSurfaceData(data); setLoading(false) })
      .catch(() => {
        // Use embedded sample data
        setSurfaceData(SAMPLE_DATA)
        setLoading(false)
      })
  }, [])
  
  return (
    <main style={{ height: '100vh', width: '100vw', background: '#000010' }}>
      <Canvas camera={{ position: [0, 0, 2.8], fov: 55 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[5, 5, 5]} intensity={0.7} />
        <pointLight position={[-5, -5, -5]} intensity={0.3} color="#0066ff" />
        
        <BosonicCube />
        
        <Suspense fallback={<LoadingSphere />}>
          {surfaceData && (
            <>
              <DisplacedSphere surfaceData={surfaceData} wireframe={viewMode === 'wireframe'} />
              <MeasuredVertices surfaceData={surfaceData} />
            </>
          )}
        </Suspense>
        
        <OrbitControls 
          enablePan={false} 
          minDistance={1.5} 
          maxDistance={6}
          autoRotate={false}
          rotateSpeed={0.5}
        />
      </Canvas>
      
      <StatsPanel 
        surfaceData={surfaceData} 
        viewMode={viewMode} 
        onViewModeChange={setViewMode} 
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
        Drag to rotate • Scroll to zoom
      </div>
      
      <Link href="/hypersphere/unified" style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        color: '#0ff',
        fontSize: 11,
        fontFamily: 'monospace',
        background: 'rgba(0,255,255,0.1)',
        padding: '8px 12px',
        borderRadius: 4,
        border: '1px solid #0ff',
        textDecoration: 'none',
      }}>
        View Unified Surface →
      </Link>
      
      <Link href="/hypersphere/visualizations" style={{
        position: 'absolute',
        bottom: 60,
        right: 20,
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
    </main>
  )
}

// =============================================================================
// SAMPLE DATA (from actual quantum measurements)
// =============================================================================

const SAMPLE_DATA: HypersphereSurfaceData = {
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
