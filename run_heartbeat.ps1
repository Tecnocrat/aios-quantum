<#
.SYNOPSIS
  AIOS Quantum Heartbeat Runner — multi-provider quantum heartbeats.

.DESCRIPTION
  Runs the quantum heartbeat scheduler from aios-quantum using Python 3.12.
  Supports multiple quantum providers with automatic failover:
    IBM Quantum → qBraid → Amazon Braket → Local Simulator
  
  Modes:
    - simulator:  Local StatevectorSampler (zero cost)
    - single:     One heartbeat via best available provider
    - scheduled:  Continuous heartbeat on interval
    - status:     Show provider availability

.PARAMETER Mode
  Execution mode: "simulator", "single", "scheduled", or "status"

.PARAMETER Provider
  Preferred provider: "ibm", "qbraid", "braket", "" (auto)

.PARAMETER Backend
  Specific backend name (e.g., "ibm_torino", "ibm_fez")

.PARAMETER Qubits
  Number of qubits (default: 5)

.PARAMETER Shots
  Number of measurement shots (default: 2048)

.PARAMETER MaxBeats
  For scheduled mode: stop after N beats (default: unlimited)

.EXAMPLE
  .\run_heartbeat.ps1 -Mode status
  .\run_heartbeat.ps1 -Mode single
  .\run_heartbeat.ps1 -Mode single -Provider ibm -Backend ibm_torino
  .\run_heartbeat.ps1 -Mode scheduled -MaxBeats 3
  .\run_heartbeat.ps1 -Mode simulator
#>

param(
    [ValidateSet("simulator", "single", "scheduled", "status")]
    [string]$Mode = "single",
    
    [string]$Provider = "",       # "" = auto (failover chain)
    [string]$Backend = "",        # "" = auto
    [int]$Qubits = 5,
    [int]$Shots = 2048,
    [int]$MaxBeats = 0,           # 0 = unlimited for scheduled
    [int]$IntervalSeconds = 3600
)

$ErrorActionPreference = "Stop"
$QuantumDir = "C:\dev\aios-quantum"
$Python312 = "C:\Users\jesus\AppData\Local\Programs\Python\Python312\python.exe"

# Verify Python 3.12
if (!(Test-Path $Python312)) {
    Write-Error "Python 3.12 not found at $Python312"
    exit 1
}

# Load .env if present
$envFile = Join-Path $QuantumDir ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([A-Z_]+)\s*=\s*(.+)\s*$") {
            [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
        }
    }
}

# Status mode — just print provider availability
if ($Mode -eq "status") {
    & $Python312 -c @"
import sys, os
sys.path.insert(0, '$($QuantumDir.Replace('\','\\'))\\src')
os.chdir('$($QuantumDir.Replace('\','\\'))')
from dotenv import load_dotenv; load_dotenv()
from aios_quantum.providers import provider_status
print(provider_status())
"@
    exit 0
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  AIOS QUANTUM HEARTBEAT" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Mode:     $Mode"
Write-Host "  Provider: $(if ($Provider) { $Provider } else { 'auto (failover chain)' })"
Write-Host "  Backend:  $(if ($Backend) { $Backend } else { 'auto' })"
Write-Host "  Qubits:   $Qubits"
Write-Host "  Shots:    $Shots"
Write-Host "  Python:   $($Python312)"

$useSimulator = if ($Mode -eq "simulator") { "True" } else { "False" }
$useRegistry = if ($Mode -eq "simulator") { "False" } else { "True" }
$prefProvider = if ($Provider) { "'$Provider'" } else { "''" }
$prefBackend = if ($Backend) { "'$Backend'" } else { "''" }

$script = @"
import sys, os
sys.path.insert(0, '$($QuantumDir.Replace('\','\\'))\\src')
os.chdir('$($QuantumDir.Replace('\','\\'))')
from dotenv import load_dotenv; load_dotenv()

from aios_quantum.heartbeat.scheduler import QuantumHeartbeat, HeartbeatConfig

config = HeartbeatConfig(
    num_qubits=$Qubits,
    shots=$Shots,
    use_simulator=$useSimulator,
    use_provider_registry=$useRegistry,
    preferred_provider=$prefProvider,
    preferred_backend=$prefBackend,
    interval_seconds=$IntervalSeconds,
    results_dir='heartbeat_results',
)
heartbeat = QuantumHeartbeat(config)
"@

switch ($Mode) {
    "simulator" {
        Write-Host "  Backend:  StatevectorSampler (local)" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Cyan
        $script += @"

result = heartbeat.single_beat()
if result:
    print(f'\nBeat #{result.beat_number} COMPLETE')
    print(f'  Backend:    {result.backend_name}')
    print(f'  Source:     {result.source}')
    print(f'  Coherence:  {result.coherence_estimate:.4f}')
    print(f'  Entropy:    {result.entropy:.4f}')
    print(f'  Time:       {result.execution_time_seconds:.3f}s')
    print(f'  Top state:  {result.top_states[0]["state"] if result.top_states else "N/A"}')
"@
    }
    "single" {
        Write-Host "  Failover: IBM -> qBraid -> Braket -> Simulator" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Cyan
        $script += @"

result = heartbeat.single_beat()
if result:
    print(f'\nBeat #{result.beat_number} COMPLETE')
    print(f'  Backend:    {result.backend_name} ({result.backend_family} {result.backend_processor})')
    print(f'  Source:     {result.source}')
    print(f'  Coherence:  {result.coherence_estimate:.4f}')
    print(f'  Entropy:    {result.entropy:.4f}')
    print(f'  Time:       {result.execution_time_seconds:.3f}s')
    print(f'  Job ID:     {result.job_id}')
    print(f'  Top state:  {result.top_states[0]["state"] if result.top_states else "N/A"}')
else:
    print('Heartbeat failed or budget exhausted')
"@
    }
    "scheduled" {
        $maxArg = if ($MaxBeats -gt 0) { $MaxBeats } else { "None" }
        Write-Host "  Failover: IBM -> qBraid -> Braket -> Simulator" -ForegroundColor Yellow
        Write-Host "  Interval: ${IntervalSeconds}s" -ForegroundColor Yellow
        Write-Host "  MaxBeats: $(if ($MaxBeats -gt 0) { $MaxBeats } else { 'unlimited' })" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Cyan
        $script += @"

heartbeat.start(max_beats=$maxArg)
"@
    }
}

& $Python312 -c $script
