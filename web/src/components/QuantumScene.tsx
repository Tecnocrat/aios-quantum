'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Line } from '@react-three/drei'
import { useRef, useMemo } from 'react'
import * as THREE from 'three'

interface HeartbeatData {
  counts: Record<string, number>
  coherence_estimate: number
}

interface Props {
  heartbeatData: HeartbeatData | null
}

// Convert quantum state to color
function stateToColor(state: string, probability: number): THREE.Color {
  // State determines hue
  const stateInt = parseInt(state, 2) || 0
  const maxVal = Math.pow(2, state.length) - 1
  const hue = maxVal > 0 ? stateInt / maxVal : 0
  
  // Probability affects saturation and lightness
  const saturation = 0.7 + 0.3 * probability
  const lightness = 0.3 + 0.4 * probability
  
  return new THREE.Color().setHSL(hue, saturation, lightness)
}

// Generate sphere surface points
function generateSpherePoints(
  radius: number, 
  resolution: number,
  counts: Record<string, number>
): { positions: Float32Array, colors: Float32Array } {
  const points: number[] = []
  const colors: number[] = []
  
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  const sortedStates = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
  
  let pointIndex = 0
  const totalPoints = resolution * resolution
  
  for (let i = 0; i < resolution; i++) {
    const theta = Math.PI * i / (resolution - 1)
    const phiCount = Math.max(1, Math.floor(resolution * Math.sin(theta)))
    
    for (let j = 0; j < phiCount; j++) {
      const phi = 2 * Math.PI * j / phiCount
      
      const x = radius * Math.sin(theta) * Math.cos(phi)
      const y = radius * Math.sin(theta) * Math.sin(phi)
      const z = radius * Math.cos(theta)
      
      points.push(x, y, z)
      
      // Determine which state this point represents
      let accumulated = 0
      let pointState = sortedStates[0]?.[0] || '00000'
      let pointProb = 0
      
      for (const [state, count] of sortedStates) {
        const statePoints = Math.floor((count / total) * totalPoints)
        accumulated += statePoints
        if (pointIndex < accumulated) {
          pointState = state
          pointProb = count / total
          break
        }
      }
      
      const color = stateToColor(pointState, pointProb)
      colors.push(color.r, color.g, color.b)
      
      pointIndex++
    }
  }
  
  return {
    positions: new Float32Array(points),
    colors: new Float32Array(colors)
  }
}

// The Sphere component
function TachyonicSphere({ heartbeatData }: Props) {
  const pointsRef = useRef<THREE.Points>(null)
  
  const { positions, colors } = useMemo(() => {
    const counts = heartbeatData?.counts || { '00000': 1 }
    return generateSpherePoints(0.8, 32, counts)
  }, [heartbeatData])
  
  useFrame((state) => {
    if (pointsRef.current) {
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
        size={0.04}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation
      />
    </points>
  )
}

// The Cube wireframe
function BosonicCube() {
  const size = 2
  const h = size / 2
  
  // Define cube edges
  const edges = [
    // Bottom face
    [[-h, -h, -h], [h, -h, -h]],
    [[h, -h, -h], [h, h, -h]],
    [[h, h, -h], [-h, h, -h]],
    [[-h, h, -h], [-h, -h, -h]],
    // Top face
    [[-h, -h, h], [h, -h, h]],
    [[h, -h, h], [h, h, h]],
    [[h, h, h], [-h, h, h]],
    [[-h, h, h], [-h, -h, h]],
    // Verticals
    [[-h, -h, -h], [-h, -h, h]],
    [[h, -h, -h], [h, -h, h]],
    [[h, h, -h], [h, h, h]],
    [[-h, h, -h], [-h, h, h]],
  ]
  
  return (
    <group>
      {edges.map((edge, i) => (
        <Line
          key={i}
          points={edge as [number, number, number][]}
          color="#00ffff"
          lineWidth={1}
          transparent
          opacity={0.3}
        />
      ))}
    </group>
  )
}

// Inner sphere (translucent)
function InnerSphere() {
  return (
    <mesh>
      <sphereGeometry args={[0.75, 32, 32]} />
      <meshBasicMaterial
        color="#001122"
        transparent
        opacity={0.2}
        side={THREE.BackSide}
      />
    </mesh>
  )
}

// Main scene
export default function QuantumScene({ heartbeatData }: Props) {
  return (
    <Canvas
      camera={{ position: [0, 0, 4], fov: 75 }}
      style={{ background: '#000011' }}
    >
      <ambientLight intensity={0.5} />
      
      <BosonicCube />
      <InnerSphere />
      <TachyonicSphere heartbeatData={heartbeatData} />
      
      <OrbitControls
        enablePan={false}
        minDistance={2}
        maxDistance={10}
        autoRotate
        autoRotateSpeed={0.5}
      />
    </Canvas>
  )
}
