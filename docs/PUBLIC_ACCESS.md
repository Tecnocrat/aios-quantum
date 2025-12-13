# Public Access & Portfolio Integration

Guide for deploying AIOS Quantum visualization and integrating with GitHub portfolio.

## Deployment Options

### Option 1: Vercel (Recommended)

Vercel provides free hosting for Next.js apps with automatic deployments.

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from web directory
cd web
vercel

# Follow prompts to link to your Vercel account
# Get public URL: https://aios-quantum.vercel.app
```

**Benefits:**
- Free tier includes custom domain
- Automatic HTTPS
- Instant deployments on git push
- Built-in analytics

### Option 2: GitHub Pages (Static Export)

For a static export that works on GitHub Pages:

```bash
# In web/next.config.mjs, add:
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  basePath: '/aios-quantum',
}

# Build static export
cd web
npm run build

# The 'out' folder contains deployable static files
```

### Option 3: Local Demo Server

For local presentations:

```bash
cd web
npm run dev
# Access at http://localhost:3000
```

---

## Portfolio Integration

### Static Snapshots for README

The visualization includes capture tools:

1. **Screenshots (PNG)**
   - Click "📸 Snapshot" button
   - Auto-downloads timestamped PNG
   - Filename format: `aios-quantum_YYYY-MM-DDTHH-MM-SS.png`

2. **Video Recording (WebM)**
   - Click "🎬 Record" to start
   - Click "⏹ Stop" to save
   - Filename format: `aios-quantum_recording_YYYY-MM-DDTHH-MM-SS.webm`

### Recommended Snapshots for Portfolio

Capture these key views:

| Snapshot | Mode | View | Purpose |
|----------|------|------|---------|
| topology_front.png | Topology Mesh | Front view | Main hero image |
| topology_angle.png | Topology Mesh | 45° angle | Show 3D depth |
| hypergate_full.png | Hypergate Sphere | Full sphere | Show experiment distribution |
| hypergate_filtered.png | Hypergate Sphere | Single class | Demonstrate filtering |

### Automated Snapshot Script

Use browser console for batch captures:

```javascript
// Access capture API
const capture = window.__quantumCapture

// Take screenshot
capture?.screenshot()

// Record 10-second clip
capture?.startRecording()
setTimeout(() => capture?.stopRecording(), 10000)
```

---

## GitHub README Integration

### Embedding Images

```markdown
## AIOS Quantum Visualization

![Topology Mesh](./docs/screenshots/topology_mesh.png)
*3D quantum-displaced surface showing error topology*

![Hypergate Sphere](./docs/screenshots/hypergate_sphere.png)
*Unified experiment visualization with class-based positioning*
```

### Live Demo Link

```markdown
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://aios-quantum.vercel.app/hypersphere/visualizations)
```

### Video Demo (GIF)

Convert WebM to GIF for GitHub:

```bash
# Using ffmpeg
ffmpeg -i aios-quantum_recording.webm -vf "fps=10,scale=600:-1" -loop 0 demo.gif
```

Then embed:
```markdown
![Quantum Visualization Demo](./docs/demo.gif)
```

---

## Screenshot Directory Structure

```
docs/
├── screenshots/
│   ├── topology_mesh.png
│   ├── topology_wireframe.png
│   ├── hypergate_sphere.png
│   ├── hypergate_filtered.png
│   └── timeline/
│       ├── 2025-12-13_session1.png
│       ├── 2025-12-14_session2.png
│       └── ...
├── videos/
│   ├── demo_rotation.webm
│   └── demo_mode_switch.webm
└── gifs/
    └── demo.gif
```

---

## Tecnocrat Portfolio Agent Integration

The portfolio agent at `Tecnocrat/Tecnocrat` can:

1. **Fetch latest snapshot** from `docs/screenshots/`
2. **Update portfolio README** with new images
3. **Track evolution** via timestamped snapshots

### Snapshot Metadata Format

Include metadata in filename or JSON sidecar:

```json
{
  "timestamp": "2025-12-13T10:30:00Z",
  "mode": "hypergate",
  "version": "v0.3-multiviz",
  "experimentCount": 16,
  "resolution": { "width": 1920, "height": 1080 }
}
```

### Webhook Integration (Optional)

Set up GitHub Actions to auto-capture:

```yaml
# .github/workflows/snapshot.yml
name: Capture Visualization Snapshot

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  snapshot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd web && npm ci && npm run build
      - name: Capture snapshot
        run: |
          # Use Playwright or Puppeteer to capture
          npx playwright screenshot http://localhost:3000 screenshot.png
      - name: Commit snapshot
        run: |
          git add docs/screenshots/
          git commit -m "📸 Weekly snapshot $(date +%Y-%m-%d)"
          git push
```

---

## Version History (Snapshot Thread)

| Date | Version | Changes | Snapshot |
|------|---------|---------|----------|
| 2025-12-11 | v0.1 | Initial 3D engine | topology_v0.1.png |
| 2025-12-12 | v0.2 | Hypersphere visualization | hypersphere_v0.2.png |
| 2025-12-13 | v0.3 | Multi-modal viz, exotic experiments | multiviz_v0.3.png |

This creates a visual evolution trail for the portfolio.
