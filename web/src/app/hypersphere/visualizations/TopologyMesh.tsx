'use client'

// =============================================================================
// TOPOLOGY MESH VISUALIZATION
// =============================================================================
// Original 3D quantum-displaced surface with error topology
// Floating quantum points affect the mesh surface creating mountains and valleys
// =============================================================================

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import * as THREE from 'three'
import { HypersphereSurfaceData, heightToColor } from './types'

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

// The quantum-displaced sphere mesh
export function DisplacedSphere({ 
  surfaceData, 
  wireframe,
  autoRotate = true,
  rotationSpeed = 0.08
}: { 
  surfaceData: HypersphereSurfaceData
  wireframe: boolean
  autoRotate?: boolean
  rotationSpeed?: number
}) {
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
    if (meshRef.current && autoRotate) {
      meshRef.current.rotation.y = state.clock.elapsedTime * rotationSpeed
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
export function MeasuredVertices({ 
  surfaceData,
  autoRotate = true,
  rotationSpeed = 0.08
}: { 
  surfaceData: HypersphereSurfaceData
  autoRotate?: boolean
  rotationSpeed?: number
}) {
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
    if (pointsRef.current && autoRotate) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * rotationSpeed
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

// Bosonic boundary cube
export function BosonicCube({ size = 1.1, color = '#00ffff', opacity = 0.25 }: {
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

// =============================================================================
// STATS PANEL FOR TOPOLOGY MODE
// =============================================================================

export function TopologyStatsPanel({ 
  surfaceData, 
  wireframe, 
  onWireframeChange 
}: { 
  surfaceData: HypersphereSurfaceData | null
  wireframe: boolean
  onWireframeChange: (v: boolean) => void 
}) {
  const Row = ({ label, value, color }: { label: string; value: string | number; color?: string }) => (
    <p style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
      <span style={{ opacity: 0.7 }}>{label}</span>
      <span style={{ color: color || '#0f0' }}>{value}</span>
    </p>
  )

  return (
    <div style={{
      background: 'rgba(0,0,20,0.92)',
      border: '1px solid #0ff',
      borderRadius: 6,
      padding: 16,
      fontFamily: 'monospace',
      color: '#0ff',
      fontSize: 11,
    }}>
      <h2 style={{ fontSize: 14, marginBottom: 8, color: '#fff', letterSpacing: 1 }}>
        TOPOLOGY MESH
      </h2>
      <p style={{ marginBottom: 10, opacity: 0.6, fontSize: 9 }}>
        Quantum-displaced surface • Error topology
      </p>
      
      {surfaceData && (
        <>
          <div style={{ marginBottom: 10 }}>
            <Row label="Vertices" value={surfaceData.vertex_count} />
            <Row label="Beats" value={surfaceData.total_beats} />
            <Row label="Mean Error" value={`${(surfaceData.statistics.mean_error * 100).toFixed(2)}%`} />
            <Row label="Max Error" value={`${(surfaceData.statistics.max_error * 100).toFixed(2)}%`} color="#ff6666" />
            <Row label="Roughness" value={surfaceData.statistics.height_variance.toFixed(4)} />
          </div>
          
          {/* Color Legend */}
          <div style={{ marginBottom: 10 }}>
            <p style={{ marginBottom: 4, fontSize: 9, opacity: 0.7 }}>Height (Error → Topology)</p>
            <div style={{ 
              height: 6,
              background: 'linear-gradient(to right, #0088cc, #888888, #ff6633)',
              borderRadius: 2
            }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, marginTop: 2, opacity: 0.6 }}>
              <span>▼ Valley (0%)</span>
              <span>Mountain ▲</span>
            </div>
          </div>
        </>
      )}
      
      {/* View Mode */}
      <div style={{ display: 'flex', gap: 4 }}>
        {[false, true].map((isWire) => (
          <button
            key={isWire ? 'wire' : 'solid'}
            onClick={() => onWireframeChange(isWire)}
            style={{
              flex: 1,
              padding: '5px 6px',
              background: wireframe === isWire ? '#0ff' : 'transparent',
              color: wireframe === isWire ? '#000' : '#0ff',
              border: '1px solid #0ff',
              borderRadius: 3,
              cursor: 'pointer',
              fontSize: 9,
              fontFamily: 'monospace',
              textTransform: 'uppercase'
            }}
          >
            {isWire ? 'Wire' : 'Solid'}
          </button>
        ))}
      </div>
    </div>
  )
}
