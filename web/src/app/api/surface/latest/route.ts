import { NextResponse } from 'next/server'
import * as fs from 'fs'
import * as path from 'path'

export async function GET() {
  try {
    // Look for hypersphere surface data in cardiogram_results
    const resultsDir = path.join(process.cwd(), '..', 'cardiogram_results')
    
    // Find the most recent hypersphere_surface file
    if (fs.existsSync(resultsDir)) {
      const files = fs.readdirSync(resultsDir)
        .filter(f => f.includes('hypersphere_surface') && f.endsWith('.json'))
        .sort()
        .reverse()
      
      if (files.length > 0) {
        const latestFile = path.join(resultsDir, files[0])
        const data = JSON.parse(fs.readFileSync(latestFile, 'utf-8'))
        return NextResponse.json(data)
      }
    }
    
    // No surface data found - return 404
    return NextResponse.json(
      { error: 'No surface data found' },
      { status: 404 }
    )
    
  } catch (error) {
    console.error('Error loading surface data:', error)
    return NextResponse.json(
      { error: 'Failed to load surface data' },
      { status: 500 }
    )
  }
}
