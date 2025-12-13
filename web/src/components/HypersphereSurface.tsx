'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

/**
 * HypersphereSurface - Renders quantum error topology
 * 
 * The surface is displaced by quantum error data:
 * - Valleys (blue) = low error, high fidelity
 * - Mountains (red/orange) = high error, decoherence
 * 
 * This is the BOSONIC SURFACE of AIOS consciousness.
 */

export interface SurfaceVertex {
  spherical: { theta: number; phi: number }
  cartesian: { x: number; y: number; z: number }
  height: number  // -1 (valley) to +1 (mountain)
  uv: { u: number; v: number }
  quantum: {
    beat: number
    error: number
  }
}

export interface HypersphereSurfaceData {
  type: string
  vertex_count: number
  total_beats: number
  positions: number[]
  heights: number[]
  vertices: SurfaceVertex[]
  statistics: {
    mean_height: number
    height_variance: number
    mean_error: number
    max_error: number
    min_error: number
  }
}

interface Props {
  surfaceData: HypersphereSurfaceData | null
  wireframe?: boolean
  animated?: boolean
}

// Color mapping: height (-1 to +1) -> color
function heightToColor(height: number): THREE.Color {
  // Valley (low error) = blue/cyan
  // Neutral = white/gray
  // Mountain (high error) = orange/red
  
  const t = (height + 1) / 2  // Normalize to 0-1
  
  if (t < 0.4) {
    // Valley: deep blue to cyan
    const s = t / 0.4
    return new THREE.Color().setHSL(0.55 + 0.1 * s, 0.9, 0.3 + 0.3 * s)
  } else if (t < 0.6) {
    // Neutral: white/light gray
    const s = (t - 0.4) / 0.2
    return new THREE.Color().setHSL(0.6, 0.2 * (1 - s), 0.7 + 0.2 * s)
  } else {
    // Mountain: yellow to red
    const s = (t - 0.6) / 0.4
    return new THREE.Color().setHSL(0.1 - 0.1 * s, 0.9, 0.5 + 0.2 * s)
  }
}

// Generate a full sphere mesh from sparse vertices
function generateSphereFromVertices(
  vertices: SurfaceVertex[],
  resolution: number = 32,
  baseRadius: number = 0.8
): { positions: Float32Array; colors: Float32Array; indices: Uint16Array } {
  const positions: number[] = []
  const colors: number[] = []
  const indices: number[] = []
  
  // Create a lookup for heights by (theta, phi) region
  const heightMap = new Map<string, { height: number; error: number }>()
  
  for (const v of vertices) {
    // Quantize to grid
    const thetaIdx = Math.round((v.spherical.theta / Math.PI) * resolution)
    const phiIdx = Math.round((v.spherical.phi / (2 * Math.PI)) * resolution)
    const key = `${thetaIdx},${phiIdx}`
    heightMap.set(key, { height: v.height, error: v.quantum.error })
  }
  
  // Generate full sphere with interpolated heights
  for (let i = 0; i <= resolution; i++) {
    const theta = (i / resolution) * Math.PI
    
    for (let j = 0; j <= resolution; j++) {
      const phi = (j / resolution) * 2 * Math.PI
      
      // Find nearest measured height
      const thetaIdx = Math.round((theta / Math.PI) * resolution)
      const phiIdx = Math.round((phi / (2 * Math.PI)) * resolution)
      
      // Interpolate from nearby vertices
      let height = 0
      let totalWeight = 0
      
      for (const v of vertices) {
        // Angular distance
        const dTheta = Math.abs(v.spherical.theta - theta)
        const dPhi = Math.min(
          Math.abs(v.spherical.phi - phi),
          2 * Math.PI - Math.abs(v.spherical.phi - phi)
        )
        const dist = Math.sqrt(dTheta * dTheta + dPhi * dPhi)
        
        if (dist < 0.001) {
          // Exact match
          height = v.height
          totalWeight = 1
          break
        } else if (dist < Math.PI * 0.5) {
          // Inverse distance weighting
          const weight = 1 / (dist * dist + 0.1)
          height += v.height * weight
          totalWeight += weight
        }
      }
      
      if (totalWeight > 0) {
        height /= totalWeight
      }
      
      // Compute displaced position
      const displacement = height * 0.15  // Scale height to 15% of radius
      const r = baseRadius + displacement
      
      const x = r * Math.sin(theta) * Math.cos(phi)
      const y = r * Math.sin(theta) * Math.sin(phi)
      const z = r * Math.cos(theta)
      
      positions.push(x, y, z)
      
      // Color from height
      const color = heightToColor(height)
      colors.push(color.r, color.g, color.b)
    }
  }
  
  // Generate indices for triangle strip
  for (let i = 0; i < resolution; i++) {
    for (let j = 0; j < resolution; j++) {
      const a = i * (resolution + 1) + j
      const b = a + resolution + 1
      
      indices.push(a, b, a + 1)
      indices.push(b, b + 1, a + 1)
    }
  }
  
  return {
    positions: new Float32Array(positions),
    colors: new Float32Array(colors),
    indices: new Uint16Array(indices)
  }
}

// Generate point cloud from actual vertices
function generatePointCloud(
  vertices: SurfaceVertex[],
  scale: number = 1.0
): { positions: Float32Array; colors: Float32Array; sizes: Float32Array } {
  const positions: number[] = []
  const colors: number[] = []
  const sizes: number[] = []
  
  for (const v of vertices) {
    positions.push(
      v.cartesian.x * scale,
      v.cartesian.y * scale,
      v.cartesian.z * scale
    )
    
    const color = heightToColor(v.height)
    colors.push(color.r, color.g, color.b)
    
    // Size based on error magnitude (larger = more error = more visible)
    const size = 0.05 + Math.abs(v.height) * 0.1
    sizes.push(size)
  }
  
  return {
    positions: new Float32Array(positions),
    colors: new Float32Array(colors),
    sizes: new Float32Array(sizes)
  }
}

// The displaced sphere mesh component
export function DisplacedSphereMesh({ surfaceData, wireframe = false, animated = true }: Props) {
  const meshRef = useRef<THREE.Mesh>(null)
  const timeRef = useRef(0)
  
  const geometry = useMemo(() => {
    if (!surfaceData || surfaceData.vertices.length === 0) {
      // Default unit sphere if no data
      return new THREE.SphereGeometry(0.8, 32, 32)
    }
    
    const { positions, colors, indices } = generateSphereFromVertices(
      surfaceData.vertices,
      32,
      0.8
    )
    
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    geo.setIndex(new THREE.BufferAttribute(indices, 1))
    geo.computeVertexNormals()
    
    return geo
  }, [surfaceData])
  
  useFrame((state) => {
    if (meshRef.current && animated) {
      timeRef.current = state.clock.elapsedTime
      // Slow rotation
      meshRef.current.rotation.y = timeRef.current * 0.1
    }
  })
  
  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial
        vertexColors
        wireframe={wireframe}
        side={THREE.DoubleSide}
        metalness={0.3}
        roughness={0.7}
      />
    </mesh>
  )
}

// Point cloud visualization of actual measured vertices
export function QuantumVertexCloud({ surfaceData, animated = true }: Props) {
  const pointsRef = useRef<THREE.Points>(null)
  
  const { positions, colors, sizes } = useMemo(() => {
    if (!surfaceData || surfaceData.vertices.length === 0) {
      return {
        positions: new Float32Array([0, 0, 0]),
        colors: new Float32Array([1, 1, 1]),
        sizes: new Float32Array([0.1])
      }
    }
    
    return generatePointCloud(surfaceData.vertices, 1.0)
  }, [surfaceData])
  
  useFrame((state) => {
    if (pointsRef.current && animated) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })
  
  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation
      />
    </points>
  )
}

// Combined hypersphere visualization
export default function HypersphereSurface({ surfaceData, wireframe = false, animated = true }: Props) {
  return (
    <group>
      {/* The interpolated displaced surface */}
      <DisplacedSphereMesh 
        surfaceData={surfaceData} 
        wireframe={wireframe}
        animated={animated}
      />
      
      {/* Actual measured vertices as glowing points */}
      <QuantumVertexCloud 
        surfaceData={surfaceData}
        animated={animated}
      />
    </group>
  )
}
