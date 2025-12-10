import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    // Look for heartbeat results in the data directory
    const dataDir = path.join(process.cwd(), '..', 'heartbeat_results')
    
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json({ error: 'No heartbeat data found' }, { status: 404 })
    }
    
    // Get all JSON files
    const files = fs.readdirSync(dataDir)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse()
    
    if (files.length === 0) {
      return NextResponse.json({ error: 'No heartbeat data found' }, { status: 404 })
    }
    
    // Read the latest file
    const latestFile = path.join(dataDir, files[0])
    const data = JSON.parse(fs.readFileSync(latestFile, 'utf-8'))
    
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load heartbeat data' },
      { status: 500 }
    )
  }
}
