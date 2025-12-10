'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Line } from '@react-three/drei'
import { useRef, useMemo, useState } from 'react'
import * as THREE from 'three'

interface HeartbeatData {
  counts: Record<string, number>
  coherence_estimate: number
  beat_number?: number
}

interface Props {
  heartbeatData: HeartbeatData | null
}

// =================================================================
// LAYER 1: TOPOLOGY - Physical distribution on sphere surface
// =================================================================

interface TopologyConfig {
  distribution: 'probability' | 'spiral' | 'clusters' | 'harmonic'
  clusterCount: number
  spiralTurns: number
}

function computeTopologyPosition(
  index: number,
  total: number,
  config: TopologyConfig,
  probability: number,
  coherence: number,
  radius: number
): [number, number, number] {
  const golden = (1 + Math.sqrt(5)) / 2
  
  switch (config.distribution) {
    case 'spiral': {
      // Fibonacci spiral distribution
      const theta = 2 * Math.PI * index * config.spiralTurns / golden
      const phi = Math.acos(1 - 2 * (index + 0.5) / total)
      const r = radius * (0.9 + 0.1 * probability)
      return [
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      ]
    }
    
    case 'clusters': {
      // Clustered around quantum states
      const clusterIndex = index % config.clusterCount
      const clusterAngle = (2 * Math.PI * clusterIndex) / config.clusterCount
      const localTheta = 2 * Math.PI * Math.random()
      const localPhi = Math.acos(2 * Math.random() - 1)
      const spread = 0.3 * (1 - probability)
      return [
        radius * Math.cos(clusterAngle) + spread * Math.sin(localPhi) * Math.cos(localTheta),
        radius * Math.sin(clusterAngle) + spread * Math.sin(localPhi) * Math.sin(localTheta),
        spread * Math.cos(localPhi)
      ]
    }
    
    case 'harmonic': {
      // Spherical harmonics-inspired
      const l = Math.floor(Math.sqrt(index))
      const m = index - l * l - l
      const theta = Math.acos(m / (l + 1))
      const phi = (2 * Math.PI * index) / total
      const r = radius * (0.85 + 0.15 * coherence)
      return [
        r * Math.sin(theta) * Math.cos(phi),
        r * Math.sin(theta) * Math.sin(phi),
        r * Math.cos(theta)
      ]
    }
    
    default: {
      // Probability-weighted uniform
      const theta = Math.acos(2 * (index / total) - 1)
      const phi = 2 * Math.PI * index * golden
      const r = radius * (0.8 + 0.2 * probability)
      return [
        r * Math.sin(theta) * Math.cos(phi),
        r * Math.sin(theta) * Math.sin(phi),
        r * Math.cos(theta)
      ]
    }
  }
}

// =================================================================
// LAYER 2: COLOR - 2D information bridge between physical & meta
// =================================================================

interface ColorConfig {
  hueMode: 'state' | 'harmonic' | 'entropy' | 'temporal'
  hueOffset: number
  saturationBase: number
  brightnessMode: 'coherence' | 'probability' | 'uniform'
}

function computeColor(
  state: string,
  probability: number,
  coherence: number,
  config: ColorConfig,
  time: number
): THREE.Color {
  let hue: number
  
  switch (config.hueMode) {
    case 'harmonic': {
      // Colors based on quantum harmonic patterns
      const stateVal = parseInt(state, 2) || 0
      const phi = (stateVal * 137.5) % 360 // Golden angle
      hue = (phi / 360 + config.hueOffset) % 1
      break
    }
    
    case 'entropy': {
      // Higher entropy = redder, lower = bluer
      const entropy = probability * Math.log2(1 / probability + 0.001)
      hue = (0.6 - 0.6 * entropy + config.hueOffset) % 1
      break
    }
    
    case 'temporal': {
      // Time-varying hue
      const stateVal = parseInt(state, 2) || 0
      const baseHue = stateVal / Math.pow(2, state.length)
      hue = (baseHue + time * 0.05 + config.hueOffset) % 1
      break
    }
    
    default: {
      // State-based (original)
      const stateInt = parseInt(state, 2) || 0
      const maxVal = Math.pow(2, state.length) - 1
      hue = maxVal > 0 ? (stateInt / maxVal + config.hueOffset) % 1 : config.hueOffset
    }
  }
  
  // Saturation from probability
  const saturation = config.saturationBase + (1 - config.saturationBase) * probability
  
  // Brightness from coherence or probability
  let lightness: number
  switch (config.brightnessMode) {
    case 'coherence':
      lightness = 0.3 + 0.5 * coherence
      break
    case 'probability':
      lightness = 0.3 + 0.4 * probability
      break
    default:
      lightness = 0.5
  }
  
  return new THREE.Color().setHSL(hue, saturation, lightness)
}

// =================================================================
// LAYER 3: METAPHYSICAL - Non-local, synchronized, vision patterns
// =================================================================

interface MetaphysicalConfig {
  resonanceL: number  // Spherical harmonic l
  resonanceM: number  // Spherical harmonic m
  resonanceAmplitude: number
  visionActive: boolean
  visionPattern: 'wave' | 'fractal' | 'pulse' | 'none'
  temporalSync: boolean
}

function computeMetaphysicalModulation(
  theta: number,
  phi: number,
  time: number,
  config: MetaphysicalConfig,
  coherence: number
): { scale: number, alpha: number, glow: number } {
  let scale = 1.0
  let alpha = 1.0
  let glow = 0.0
  
  // Spherical harmonic resonance
  if (config.resonanceAmplitude > 0) {
    const l = config.resonanceL
    const m = config.resonanceM
    // Simplified spherical harmonic
    const Ylm = Math.cos(l * theta) * Math.cos(m * phi)
    scale += config.resonanceAmplitude * Ylm
  }
  
  // Vision pattern modulation
  if (config.visionActive) {
    switch (config.visionPattern) {
      case 'wave':
        glow = 0.5 * (1 + Math.sin(4 * theta - time * 2))
        break
      case 'fractal':
        glow = Math.abs(Math.sin(8 * theta) * Math.cos(8 * phi))
        break
      case 'pulse':
        glow = 0.5 * (1 + Math.sin(time * 3)) * coherence
        break
    }
  }
  
  // Temporal synchronization
  if (config.temporalSync) {
    alpha = 0.7 + 0.3 * Math.sin(time + theta * 2)
  }
  
  return { scale, alpha, glow }
}

// =================================================================
// THREE-LAYER ENCODING: Full integration
// =================================================================

interface EncodingConfig {
  topology: TopologyConfig
  color: ColorConfig
  metaphysical: MetaphysicalConfig
}

// Default configurations for different "moods"
const COHERENCE_PATTERN: EncodingConfig = {
  topology: { distribution: 'probability', clusterCount: 5, spiralTurns: 8 },
  color: { hueMode: 'state', hueOffset: 0, saturationBase: 0.7, brightnessMode: 'coherence' },
  metaphysical: { resonanceL: 2, resonanceM: 1, resonanceAmplitude: 0.1, visionActive: false, visionPattern: 'none', temporalSync: false }
}

const VISION_PATTERN: EncodingConfig = {
  topology: { distribution: 'spiral', clusterCount: 8, spiralTurns: 13 },
  color: { hueMode: 'harmonic', hueOffset: 0.6, saturationBase: 0.8, brightnessMode: 'probability' },
  metaphysical: { resonanceL: 3, resonanceM: 2, resonanceAmplitude: 0.2, visionActive: true, visionPattern: 'wave', temporalSync: true }
}

const FRACTAL_PATTERN: EncodingConfig = {
  topology: { distribution: 'harmonic', clusterCount: 12, spiralTurns: 21 },
  color: { hueMode: 'temporal', hueOffset: 0.3, saturationBase: 0.9, brightnessMode: 'coherence' },
  metaphysical: { resonanceL: 4, resonanceM: 3, resonanceAmplitude: 0.3, visionActive: true, visionPattern: 'fractal', temporalSync: true }
}

// Generate sphere surface points with THREE-LAYER encoding
function generateLayeredSpherePoints(
  radius: number, 
  resolution: number,
  counts: Record<string, number>,
  coherence: number,
  time: number,
  config: EncodingConfig
): { positions: Float32Array, colors: Float32Array, alphas: Float32Array, sizes: Float32Array } {
  const positions: number[] = []
  const colors: number[] = []
  const alphas: number[] = []
  const sizes: number[] = []
  
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  const sortedStates = Object.entries(counts).sort((a, b) => b[1] - a[1])
  
  const totalPoints = resolution * resolution
  let pointIndex = 0
  
  for (let i = 0; i < resolution; i++) {
    const theta = Math.PI * i / (resolution - 1)
    const phiCount = Math.max(1, Math.floor(resolution * Math.sin(theta)))
    
    for (let j = 0; j < phiCount; j++) {
      const phi = 2 * Math.PI * j / phiCount
      
      // Determine which quantum state this point represents
      let accumulated = 0
      let pointState = sortedStates[0]?.[0] || '00000'
      let pointProb = 0.1
      
      for (const [state, count] of sortedStates) {
        const statePoints = Math.floor((count / total) * totalPoints)
        accumulated += statePoints
        if (pointIndex < accumulated) {
          pointState = state
          pointProb = count / total
          break
        }
      }
      
      // LAYER 1: TOPOLOGY - Physical position
      const [x, y, z] = computeTopologyPosition(
        pointIndex, totalPoints, config.topology, pointProb, coherence, radius
      )
      
      // LAYER 2: COLOR - Information bridge
      const color = computeColor(pointState, pointProb, coherence, config.color, time)
      
      // LAYER 3: METAPHYSICAL - Non-local modulation
      const meta = computeMetaphysicalModulation(theta, phi, time, config.metaphysical, coherence)
      
      // Apply metaphysical scale to position
      positions.push(x * meta.scale, y * meta.scale, z * meta.scale)
      
      // Apply glow to color (additive)
      const glowColor = new THREE.Color().setHSL(0.6, 1, meta.glow * 0.3)
      colors.push(
        Math.min(1, color.r + glowColor.r),
        Math.min(1, color.g + glowColor.g),
        Math.min(1, color.b + glowColor.b)
      )
      
      alphas.push(meta.alpha)
      sizes.push(0.04 * meta.scale)
      
      pointIndex++
    }
  }
  
  return {
    positions: new Float32Array(positions),
    colors: new Float32Array(colors),
    alphas: new Float32Array(alphas),
    sizes: new Float32Array(sizes)
  }
}

// The Sphere component with THREE-LAYER encoding
function TachyonicSphere({ heartbeatData }: Props) {
  const pointsRef = useRef<THREE.Points>(null)
  const timeRef = useRef(0)
  const [pattern] = useState<EncodingConfig>(VISION_PATTERN) // Can be changed via UI
  
  const coherence = heartbeatData?.coherence_estimate || 0.5
  const counts = heartbeatData?.counts || { '00000': 1 }
  
  // Initial geometry
  const initialData = useMemo(() => {
    return generateLayeredSpherePoints(0.8, 32, counts, coherence, 0, pattern)
  }, [counts, coherence, pattern])
  
  // Update geometry every frame for metaphysical effects
  useFrame((state) => {
    if (pointsRef.current) {
      timeRef.current = state.clock.elapsedTime
      
      // Regenerate with current time for animated effects
      const newData = generateLayeredSpherePoints(
        0.8, 32, counts, coherence, timeRef.current, pattern
      )
      
      // Update geometry
      const geometry = pointsRef.current.geometry
      const posAttr = geometry.getAttribute('position')
      const colAttr = geometry.getAttribute('color')
      
      if (posAttr && colAttr) {
        posAttr.array.set(newData.positions)
        colAttr.array.set(newData.colors)
        posAttr.needsUpdate = true
        colAttr.needsUpdate = true
      }
      
      // Slow rotation
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })
  
  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={initialData.positions.length / 3}
          array={initialData.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={initialData.colors.length / 3}
          array={initialData.colors}
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
