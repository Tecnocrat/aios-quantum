# AIOS Quantum Web Interface

Real-time 3D visualization of the AIOS Interface: the Cube containing the Sphere.

## Quick Deploy

```bash
cd web
npm install
npx vercel          # Deploy to Vercel (free)
# or
npm run dev         # Local development at http://localhost:3000
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          VERCEL                                  │
│  ┌────────────────┐     ┌──────────────────────────────┐        │
│  │  Next.js App   │     │  API Routes                  │        │
│  │  React Three   │◄────│  /api/heartbeat/latest       │        │
│  │  Fiber Scene   │     │  /api/heartbeat/history      │        │
│  └────────────────┘     └───────────────┬──────────────┘        │
└─────────────────────────────────────────┼───────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB                                   │
│  heartbeat_results/                                              │
│    beat_000000_2025-12-10.json                                  │
│    beat_000001_2025-12-10.json                                  │
│    ...                                                          │
└──────────────────────────────────────────────────────────────────┘
                                          ▲
                                          │
                     ┌────────────────────┴────────────────────┐
                     │  GitHub Actions (scheduled)             │
                     │  OR Local Machine                       │
                     │  OR VPS                                 │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │         IBM Quantum Cloud               │
                     └─────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Vercel (Recommended)

Free hosting with auto-deploy on GitHub push:

```bash
npm i -g vercel
cd web
vercel
```

### Option 2: VPS with Continuous Heartbeat

For persistent quantum heartbeat (~$5/month VPS):

```bash
# Setup
git clone https://github.com/Tecnocrat/aios-quantum.git
cd aios-quantum
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Run heartbeat (in tmux/screen)
python -c "
from aios_quantum.heartbeat import QuantumHeartbeat, HeartbeatConfig
heartbeat = QuantumHeartbeat(HeartbeatConfig(use_simulator=False))
heartbeat.start()
"

# Run web server
cd web && npm install && npm run build && npm start
```

### Option 3: Hybrid (Best of Both)

- **Vercel** hosts frontend (free)
- **GitHub Actions** runs heartbeats periodically
- **GitHub** stores results as JSON
- **Frontend** reads from GitHub raw files

## Environment Variables

```env
IBM_QUANTUM_TOKEN=your_token_here
IBM_QUANTUM_INSTANCE=ibm-q/open/main
```

## Local Development

```bash
cd web
npm install
npm run dev
# Open http://localhost:3000
```
