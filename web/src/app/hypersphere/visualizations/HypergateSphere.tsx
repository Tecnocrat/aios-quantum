'use client'

// =============================================================================
// HYPERGATE SPHERE VISUALIZATION
// =============================================================================
// Dark sphere with orthogonal entry gates (hypergates)
// Experiments float at positions based on class topology
// Features: equatorial ring, north/south pole markers, class-colored vertices
// =============================================================================

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import * as THREE from 'three'
import { UnifiedSurface, CLASS_COLORS, CLASS_ICONS } from './types'

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

// Bosonic boundary cube
export function BosonicCube({ size = 1.3, color = '#0066aa', opacity = 0.2 }: {
  size?: number
  color?: string
  opacity?: number
}) {
  const h = size
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
        <Line key={i} points={edge} color={color} lineWidth={1} transparent opacity={opacity} />
      ))}
    </group>
  )
}

// Reference sphere (ghost sphere showing ideal boundary)
export function ReferenceSphere({ color = '#003366', opacity = 0.08 }: {
  color?: string
  opacity?: number
}) {
  return (
    <mesh>
      <sphereGeometry args={[1.0, 32, 32]} />
      <meshBasicMaterial color={color} wireframe transparent opacity={opacity} />
    </mesh>
  )
}

// Topology regions (north pole = consciousness, equator = computation, south pole = constants)
export function TopologyRegions() {
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

// Experiment vertices as glowing spheres
export function ExperimentVertices({ 
  surfaceData, 
  selectedClass,
  autoRotate = true,
  rotationSpeed = 0.05
}: { 
  surfaceData: UnifiedSurface
  selectedClass: string | null 
  autoRotate?: boolean
  rotationSpeed?: number
}) {
  const groupRef = useRef<THREE.Group>(null)
  
  const filteredVertices = useMemo(() => {
    if (!selectedClass) return surfaceData.vertices
    return surfaceData.vertices.filter(v => v.metadata.class === selectedClass)
  }, [surfaceData.vertices, selectedClass])
  
  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.elapsedTime * rotationSpeed
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
export function ExperimentConnections({ 
  surfaceData,
  autoRotate = true,
  rotationSpeed = 0.05
}: { 
  surfaceData: UnifiedSurface
  autoRotate?: boolean
  rotationSpeed?: number
}) {
  const groupRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.elapsedTime * rotationSpeed
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

// =============================================================================
// STATS PANEL FOR HYPERGATE MODE
// =============================================================================

export function HypergateStatsPanel({ 
  surfaceData, 
  selectedClass,
  onSelectClass
}: { 
  surfaceData: UnifiedSurface | null
  selectedClass: string | null
  onSelectClass: (cls: string | null) => void
}) {
  const Row = ({ label, value, color }: { label: string; value: string | number; color?: string }) => (
    <p style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
      <span style={{ opacity: 0.7 }}>{label}</span>
      <span style={{ color: color || '#0f0' }}>{value}</span>
    </p>
  )

  if (!surfaceData) return null
  
  const stats = surfaceData.statistics

  return (
    <div style={{
      background: 'rgba(0,0,20,0.92)',
      border: '1px solid #ff00ff',
      borderRadius: 6,
      padding: 16,
      fontFamily: 'monospace',
      color: '#ff00ff',
      fontSize: 11,
    }}>
      <h2 style={{ fontSize: 14, marginBottom: 8, color: '#fff', letterSpacing: 1 }}>
        HYPERGATE SPHERE
      </h2>
      <p style={{ marginBottom: 10, opacity: 0.6, fontSize: 9 }}>
        Orthogonal entry gates • Class topology
      </p>
      
      {/* Statistics */}
      <div style={{ marginBottom: 12 }}>
        <Row label="Total Experiments" value={stats.total} />
        <Row label="Vertices" value={surfaceData.vertex_count} />
        <Row label="Connections" value={surfaceData.edge_count} />
      </div>
      
      {/* Class Filter */}
      <div style={{ marginBottom: 10 }}>
        <p style={{ marginBottom: 6, fontSize: 9, opacity: 0.7 }}>EXPERIMENT CLASSES</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          <button
            onClick={() => onSelectClass(null)}
            style={{
              padding: '3px 6px',
              background: selectedClass === null ? '#ff00ff' : 'transparent',
              color: selectedClass === null ? '#000' : '#ff00ff',
              border: '1px solid #ff00ff',
              borderRadius: 3,
              cursor: 'pointer',
              fontSize: 8,
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
                padding: '3px 6px',
                background: selectedClass === cls ? CLASS_COLORS[cls] : 'transparent',
                color: selectedClass === cls ? '#000' : CLASS_COLORS[cls] || '#ff00ff',
                border: `1px solid ${CLASS_COLORS[cls] || '#ff00ff'}`,
                borderRadius: 3,
                cursor: 'pointer',
                fontSize: 8,
                fontFamily: 'monospace',
              }}
            >
              {CLASS_ICONS[cls] || '•'} {cls} ({count})
            </button>
          ))}
        </div>
      </div>
      
      {/* Origin breakdown */}
      <div>
        <p style={{ marginBottom: 4, fontSize: 9, opacity: 0.7 }}>ORIGIN</p>
        {Object.entries(stats.by_origin).map(([origin, count]) => (
          <Row 
            key={origin} 
            label={origin === 'ibm_quantum' ? '🔵 IBM' : '⚪ Sim'} 
            value={count}
            color={origin === 'ibm_quantum' ? '#0088ff' : '#888888'}
          />
        ))}
      </div>
    </div>
  )
}
