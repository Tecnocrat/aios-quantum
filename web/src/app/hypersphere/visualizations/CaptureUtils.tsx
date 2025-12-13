'use client'

// =============================================================================
// QUANTUM VISUALIZATION - CAPTURE UTILITIES
// =============================================================================
// Screenshot and video recording capabilities for portfolio snapshots
// Exports timestamped PNG images and WebM video recordings
// =============================================================================

import { useRef, useState, useCallback, useEffect } from 'react'
import { useThree } from '@react-three/fiber'

// =============================================================================
// TYPES
// =============================================================================

export interface CaptureMetadata {
  timestamp: string
  mode: string
  experimentCount: number
  version: string
  resolution: { width: number; height: number }
}

export interface SnapshotResult {
  dataUrl: string
  filename: string
  metadata: CaptureMetadata
}

// =============================================================================
// SCREENSHOT CAPTURE HOOK
// =============================================================================

export function useScreenshotCapture() {
  const { gl, scene, camera } = useThree()
  
  const captureScreenshot = useCallback((metadata: Partial<CaptureMetadata> = {}): SnapshotResult => {
    // Render current frame
    gl.render(scene, camera)
    
    // Get canvas data
    const dataUrl = gl.domElement.toDataURL('image/png', 1.0)
    
    // Generate timestamp
    const now = new Date()
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19)
    
    // Build filename
    const mode = metadata.mode || 'quantum-viz'
    const filename = `aios-quantum_${mode}_${timestamp}.png`
    
    // Full metadata
    const fullMetadata: CaptureMetadata = {
      timestamp: now.toISOString(),
      mode: mode,
      experimentCount: metadata.experimentCount || 0,
      version: metadata.version || 'v0.3-multiviz',
      resolution: {
        width: gl.domElement.width,
        height: gl.domElement.height
      }
    }
    
    return { dataUrl, filename, metadata: fullMetadata }
  }, [gl, scene, camera])
  
  const downloadScreenshot = useCallback((metadata: Partial<CaptureMetadata> = {}) => {
    const result = captureScreenshot(metadata)
    
    // Create download link
    const link = document.createElement('a')
    link.href = result.dataUrl
    link.download = result.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Also log metadata for reference
    console.log('📸 Screenshot captured:', result.metadata)
    
    return result
  }, [captureScreenshot])
  
  return { captureScreenshot, downloadScreenshot }
}

// =============================================================================
// VIDEO RECORDING HOOK
// =============================================================================

export function useVideoRecording() {
  const { gl } = useThree()
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  
  const startRecording = useCallback((options: { 
    fps?: number
    bitrate?: number 
  } = {}) => {
    const canvas = gl.domElement
    const stream = canvas.captureStream(options.fps || 30)
    
    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
      ? 'video/webm;codecs=vp9'
      : 'video/webm'
    
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: options.bitrate || 5000000 // 5 Mbps
    })
    
    chunksRef.current = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data)
      }
    }
    
    mediaRecorder.start(100) // Capture every 100ms
    mediaRecorderRef.current = mediaRecorder
    setIsRecording(true)
    setRecordingDuration(0)
    
    // Start duration timer
    timerRef.current = setInterval(() => {
      setRecordingDuration(d => d + 1)
    }, 1000)
    
    console.log('🎬 Recording started')
  }, [gl])
  
  const stopRecording = useCallback((): Promise<{ blob: Blob; filename: string }> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current
      if (!mediaRecorder) {
        throw new Error('No recording in progress')
      }
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        
        // Generate filename
        const now = new Date()
        const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19)
        const filename = `aios-quantum_recording_${timestamp}.webm`
        
        console.log('🎬 Recording stopped:', {
          duration: recordingDuration,
          size: `${(blob.size / 1024 / 1024).toFixed(2)} MB`
        })
        
        setIsRecording(false)
        resolve({ blob, filename })
      }
      
      mediaRecorder.stop()
    })
  }, [recordingDuration])
  
  const downloadRecording = useCallback(async () => {
    const { blob, filename } = await stopRecording()
    
    // Create download link
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    return { blob, filename }
  }, [stopRecording])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop()
      }
    }
  }, [isRecording])
  
  return {
    isRecording,
    recordingDuration,
    startRecording,
    stopRecording,
    downloadRecording
  }
}

// =============================================================================
// CAPTURE CONTROLS UI COMPONENT
// =============================================================================

export function CaptureControls({ 
  mode,
  experimentCount,
  onCapture 
}: {
  mode: string
  experimentCount: number
  onCapture?: (result: SnapshotResult) => void
}) {
  // This component should be placed INSIDE the Canvas
  const { captureScreenshot, downloadScreenshot } = useScreenshotCapture()
  const { 
    isRecording, 
    recordingDuration, 
    startRecording, 
    downloadRecording 
  } = useVideoRecording()
  
  const handleScreenshot = useCallback(() => {
    const result = downloadScreenshot({ mode, experimentCount })
    onCapture?.(result)
  }, [mode, experimentCount, downloadScreenshot, onCapture])
  
  const handleRecordToggle = useCallback(() => {
    if (isRecording) {
      downloadRecording()
    } else {
      startRecording({ fps: 30 })
    }
  }, [isRecording, startRecording, downloadRecording])
  
  // Expose methods globally for external control
  useEffect(() => {
    (window as any).__quantumCapture = {
      screenshot: () => downloadScreenshot({ mode, experimentCount }),
      startRecording: () => startRecording({ fps: 30 }),
      stopRecording: downloadRecording
    }
    return () => {
      delete (window as any).__quantumCapture
    }
  }, [mode, experimentCount, downloadScreenshot, startRecording, downloadRecording])
  
  return null // UI is external via HTML
}

// =============================================================================
// EXTERNAL CAPTURE BUTTON PANEL (HTML overlay)
// =============================================================================

export function CapturePanel({ 
  isRecording,
  recordingDuration,
  onScreenshot,
  onRecordToggle
}: {
  isRecording: boolean
  recordingDuration: number
  onScreenshot: () => void
  onRecordToggle: () => void
}) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div style={{
      position: 'absolute',
      bottom: 70,
      right: 20,
      display: 'flex',
      gap: 8,
      fontFamily: 'monospace',
      fontSize: 10,
    }}>
      {/* Screenshot button */}
      <button
        onClick={onScreenshot}
        style={{
          padding: '8px 12px',
          background: 'rgba(0,255,136,0.15)',
          color: '#00ff88',
          border: '1px solid #00ff88',
          borderRadius: 4,
          cursor: 'pointer',
          fontFamily: 'monospace',
          fontSize: 10,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
        title="Take screenshot (PNG)"
      >
        📸 Snapshot
      </button>
      
      {/* Record button */}
      <button
        onClick={onRecordToggle}
        style={{
          padding: '8px 12px',
          background: isRecording ? 'rgba(255,0,0,0.2)' : 'rgba(255,136,0,0.15)',
          color: isRecording ? '#ff4444' : '#ff8800',
          border: `1px solid ${isRecording ? '#ff4444' : '#ff8800'}`,
          borderRadius: 4,
          cursor: 'pointer',
          fontFamily: 'monospace',
          fontSize: 10,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          minWidth: 100,
        }}
        title={isRecording ? 'Stop recording' : 'Start recording (WebM)'}
      >
        {isRecording ? (
          <>
            <span style={{ 
              width: 8, 
              height: 8, 
              background: '#ff4444', 
              borderRadius: 2,
              animation: 'pulse 1s infinite'
            }} />
            {formatDuration(recordingDuration)}
          </>
        ) : (
          <>🎬 Record</>
        )}
      </button>
      
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  )
}

// =============================================================================
// BATCH SNAPSHOT UTILITY (for automated portfolio capture)
// =============================================================================

export async function captureVisualizationBatch(
  modes: string[],
  switchMode: (mode: string) => Promise<void>,
  captureScreenshot: () => SnapshotResult,
  delayMs: number = 2000
): Promise<SnapshotResult[]> {
  const results: SnapshotResult[] = []
  
  for (const mode of modes) {
    await switchMode(mode)
    // Wait for render to stabilize
    await new Promise(resolve => setTimeout(resolve, delayMs))
    const result = captureScreenshot()
    results.push(result)
    console.log(`📸 Captured: ${mode}`)
  }
  
  return results
}
