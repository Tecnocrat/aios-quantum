# AIOS Quantum Web Interface

The online visualization of the AIOS Interface: Cube containing Sphere.

## Deployment Options

### Option 1: Vercel (Recommended for Start)

```bash
cd web
npm install
npx vercel
```

Vercel will:
- Build the Next.js app
- Deploy to a `.vercel.app` URL
- Auto-deploy on every GitHub push

**Cost**: FREE for basic usage

### Option 2: VPS with Continuous Heartbeat

For a VPS (DigitalOcean, Linode, Hetzner ~$5/month):

```bash
# On VPS
git clone https://github.com/Tecnocrat/aios-quantum.git
cd aios-quantum

# Setup Python environment
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run heartbeat scheduler (in tmux or systemd)
python -c "
from aios_quantum.heartbeat import QuantumHeartbeat, HeartbeatConfig
config = HeartbeatConfig(use_simulator=True)  # or False for real hardware
heartbeat = QuantumHeartbeat(config)
heartbeat.start()
"

# In another terminal, run the web server
cd web
npm install
npm run build
npm start
```

### Option 3: Hybrid (Best of Both)

1. **Vercel** hosts the web frontend (free)
2. **GitHub Actions** runs heartbeats periodically
3. **GitHub** stores heartbeat results as JSON files
4. **Vercel** reads from GitHub raw files

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        VERCEL                               │
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │   Next.js App   │    │   API Routes                │    │
│  │                 │    │   /api/heartbeat/latest     │    │
│  │   React Three   │◄───│   /api/heartbeat/history    │    │
│  │   Fiber Scene   │    │                             │    │
│  └─────────────────┘    └──────────────┬──────────────┘    │
│                                        │                    │
└────────────────────────────────────────┼────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       GITHUB                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  heartbeat_results/                                  │   │
│  │    beat_000000_2025-12-10.json                      │   │
│  │    beat_000001_2025-12-10.json                      │   │
│  │    ...                                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                              ▲                              │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   GitHub Actions    │
                    │   (scheduled)       │
                    │   OR                │
                    │   Local Machine     │
                    │   OR                │
                    │   VPS               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    IBM Quantum      │
                    │    Cloud            │
                    └─────────────────────┘
```

## Quick Deploy to Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   cd web
   vercel
   ```

3. Set up automatic deploys:
   - Connect GitHub repo to Vercel
   - Every push auto-deploys

## Environment Variables

For production with real IBM Quantum:

```env
IBM_QUANTUM_TOKEN=your_token_here
IBM_QUANTUM_INSTANCE=ibm-q/open/main
```

## Local Development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000
