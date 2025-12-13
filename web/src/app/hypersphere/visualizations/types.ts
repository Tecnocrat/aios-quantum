// =============================================================================
// QUANTUM VISUALIZATION - MODULAR TYPE SYSTEM
// =============================================================================
// Multi-modal visualization registry supporting different quantum data views
// =============================================================================

import { ReactNode } from 'react'

// =============================================================================
// VISUALIZATION MODES
// =============================================================================

export type VisualizationMode = 
  | 'topology'       // Original: 3D mesh with quantum-displaced surface
  | 'unified'        // New: Dark sphere with hypergates and floating experiments
  | 'experiments'    // NEW: All experiments cloud from compiled data
  | 'constellation'  // Future: Star map of quantum states
  | 'timeline'       // Future: Temporal flow visualization
  | 'network'        // Future: Entanglement network graph
  | 'cardiogram'     // Future: EKG-style heartbeat waveform

export interface VisualizationModeConfig {
  id: VisualizationMode
  name: string
  description: string
  icon: string
  color: string
  dataSource: 'surface' | 'unified' | 'heartbeat' | 'both'
  available: boolean
  preview?: string  // Preview image/gradient
}

export const VISUALIZATION_MODES: VisualizationModeConfig[] = [
  {
    id: 'experiments',
    name: 'Experiment Cloud',
    description: 'ALL quantum experiments from GitHub, IBM Quantum, and local files. 124+ data points.',
    icon: '☁️',
    color: '#00ffff',
    dataSource: 'both',
    available: true,
    preview: 'linear-gradient(135deg, #000022 0%, #001144 50%, #00ffff 100%)'
  },
  {
    id: 'topology',
    name: 'Topology Mesh',
    description: '3D quantum-displaced surface with error topology. Floating quantum points affect the mesh surface.',
    icon: '🌐',
    color: '#00ffff',
    dataSource: 'surface',
    available: true,
    preview: 'linear-gradient(135deg, #001133 0%, #003366 50%, #00ffff 100%)'
  },
  {
    id: 'unified',
    name: 'Hypergate Sphere',
    description: 'Dark sphere with orthogonal entry gates. Experiments float at positions based on class topology.',
    icon: '🔮',
    color: '#ff00ff',
    dataSource: 'unified',
    available: true,
    preview: 'linear-gradient(135deg, #000022 0%, #220044 50%, #ff00ff 100%)'
  },
  {
    id: 'constellation',
    name: 'Quantum Constellation',
    description: 'Star map visualization connecting experiments by entanglement and coherence relationships.',
    icon: '✨',
    color: '#ffcc00',
    dataSource: 'unified',
    available: false,
    preview: 'linear-gradient(135deg, #000011 0%, #111100 50%, #ffcc00 100%)'
  },
  {
    id: 'timeline',
    name: 'Temporal Flow',
    description: 'Time-based river visualization showing experiment evolution and quantum state changes.',
    icon: '🌊',
    color: '#00ff88',
    dataSource: 'both',
    available: false,
    preview: 'linear-gradient(135deg, #001100 0%, #003322 50%, #00ff88 100%)'
  },
  {
    id: 'network',
    name: 'Entanglement Web',
    description: 'Force-directed graph showing quantum correlations and entanglement links.',
    icon: '🕸️',
    color: '#ff8800',
    dataSource: 'unified',
    available: false,
    preview: 'linear-gradient(135deg, #110500 0%, #331100 50%, #ff8800 100%)'
  },
  {
    id: 'cardiogram',
    name: 'Quantum Cardiogram',
    description: 'EKG-style waveform display of heartbeat sequences and error rhythms.',
    icon: '💓',
    color: '#ff0066',
    dataSource: 'heartbeat',
    available: false,
    preview: 'linear-gradient(135deg, #110011 0%, #330022 50%, #ff0066 100%)'
  }
]

// =============================================================================
// DATA TYPES - SHARED ACROSS VISUALIZATIONS
// =============================================================================

// Original surface format (for topology mesh)
export interface SurfaceVertex {
  spherical: { theta: number; phi: number }
  cartesian: { x: number; y: number; z: number }
  height: number
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

// Unified surface format (for hypergate sphere and others)
export interface UnifiedVertex {
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

export interface UnifiedSurface {
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
// COLOR SYSTEMS
// =============================================================================

export const CLASS_COLORS: Record<string, string> = {
  heartbeat: '#00ffff',
  cardiogram: '#0088ff',
  arithmetic: '#00ff88',
  search: '#00ffaa',
  factoring: '#88ff00',
  entanglement: '#ff00ff',
  teleportation: '#ff88ff',
  simulation: '#8800ff',
  pi_search: '#ff8800',
  golden: '#ffcc00',
  random: '#888888',
  calibration: '#ffffff',
  error: '#ff0000',
  witness: '#00ffcc',
}

export const CLASS_ICONS: Record<string, string> = {
  heartbeat: '💓',
  cardiogram: '📊',
  arithmetic: '➕',
  search: '🔍',
  entanglement: '🔮',
  pi_search: 'π',
  golden: 'φ',
  random: '🎲',
  teleportation: '⚡',
  simulation: '🧪',
  calibration: '⚙️',
  witness: '👁️',
}

// =============================================================================
// SOURCE AND BACKEND FILTERS
// =============================================================================

export type SourceFilter = 'all' | 'simulation' | 'real'

export type BackendFamily = 'all' | 'eagle' | 'heron' | 'falcon' | 'simulator' | 'unknown'

export interface HeartbeatFilters {
  source: SourceFilter
  backendFamily: BackendFamily
  selectedBackends: string[]  // Specific backends like ['ibm_brisbane', 'ibm_fez']
}

export const DEFAULT_FILTERS: HeartbeatFilters = {
  source: 'all',
  backendFamily: 'all',
  selectedBackends: []
}

// Backend family metadata for UI
export const BACKEND_FAMILIES: Record<BackendFamily, { name: string; color: string; qubits: number }> = {
  all: { name: 'All Backends', color: '#ffffff', qubits: 0 },
  eagle: { name: 'Eagle (127q)', color: '#00ff88', qubits: 127 },
  heron: { name: 'Heron (133q)', color: '#ff00ff', qubits: 133 },
  falcon: { name: 'Falcon (27q)', color: '#ffcc00', qubits: 27 },
  simulator: { name: 'Simulator', color: '#888888', qubits: 0 },
  unknown: { name: 'Unknown', color: '#444444', qubits: 0 }
}

// Individual backend metadata
export const IBM_BACKENDS: Record<string, { family: BackendFamily; processor: string; qubits: number }> = {
  ibm_brisbane: { family: 'eagle', processor: 'r3', qubits: 127 },
  ibm_kyoto: { family: 'eagle', processor: 'r3', qubits: 127 },
  ibm_osaka: { family: 'eagle', processor: 'r3', qubits: 127 },
  ibm_sherbrooke: { family: 'eagle', processor: 'r3', qubits: 127 },
  ibm_fez: { family: 'heron', processor: 'r1', qubits: 133 },
  ibm_torino: { family: 'heron', processor: 'r1', qubits: 133 },
  ibm_marrakesh: { family: 'heron', processor: 'r2', qubits: 133 },
  statevector_sampler: { family: 'simulator', processor: '', qubits: 0 },
  aer_simulator: { family: 'simulator', processor: '', qubits: 0 },
}

// =============================================================================
// SHARED VISUALIZATION CONTROLS
// =============================================================================

export interface VisualizationControls {
  wireframe: boolean
  showVertices: boolean
  showConnections: boolean
  autoRotate: boolean
  rotationSpeed: number
  selectedClass: string | null
  cameraPosition: [number, number, number]
  // Heartbeat source filters
  sourceFilter: SourceFilter
  backendFilter: BackendFamily
  selectedBackends: string[]
}

export const DEFAULT_CONTROLS: VisualizationControls = {
  wireframe: false,
  showVertices: true,
  showConnections: true,
  autoRotate: true,
  rotationSpeed: 0.05,
  selectedClass: null,
  cameraPosition: [0, 0, 3.5],
  // Default filter settings
  sourceFilter: 'all',
  backendFilter: 'all',
  selectedBackends: []
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

export function heightToColor(height: number): { r: number; g: number; b: number } {
  const t = (height + 1) / 2
  
  if (t < 0.4) {
    const s = t / 0.4
    const h = 0.55 + 0.1 * s
    const sat = 0.9
    const l = 0.3 + 0.3 * s
    return hslToRgb(h, sat, l)
  } else if (t < 0.6) {
    return hslToRgb(0.55, 0.3, 0.7)
  } else {
    const s = (t - 0.6) / 0.4
    const h = 0.08 - 0.08 * s
    const sat = 0.9
    const l = 0.5 + 0.15 * s
    return hslToRgb(h, sat, l)
  }
}

function hslToRgb(h: number, s: number, l: number): { r: number; g: number; b: number } {
  let r: number, g: number, b: number

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

  return { r, g, b }
}
