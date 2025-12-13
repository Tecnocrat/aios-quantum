#!/usr/bin/env python
"""
QUANTUM EXPERIMENT TRACKER
==========================

Extracts and compiles ALL quantum experiment data from:
1. GitHub Actions workflow runs (heartbeat.yml)
2. IBM Quantum job history (via API)
3. Local result files (cardiogram_results/, quantum_jobs/results/)

Outputs unified dataset for hypersphere visualization.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()


@dataclass
class QuantumExperiment:
    """Unified representation of a quantum experiment."""
    
    # Identity
    id: str                     # Unique identifier
    source: str                 # 'github', 'ibm_quantum', 'local'
    experiment_type: str        # 'heartbeat', 'cardiogram', 'pi_pulse', 'consciousness', etc.
    
    # Execution
    backend: str                # 'ibm_torino', 'ibm_fez', 'simulator'
    timestamp: str              # ISO timestamp
    status: str                 # 'success', 'failure', 'cancelled'
    
    # Circuit
    num_qubits: int = 0
    circuit_depth: int = 0
    shots: int = 0
    
    # Results
    coherence: float = 0.0      # Primary metric
    entropy: float = 0.0
    fidelity: float = 0.0
    error_rate: float = 0.0
    
    # Raw data reference
    counts: Optional[Dict[str, int]] = None
    raw_file: Optional[str] = None
    
    # Hypersphere mapping
    theta: float = 0.0          # Polar angle
    phi: float = 0.0            # Azimuthal angle  
    radius: float = 1.0         # Distance from center
    hue: float = 0.5            # Color hue [0-1]
    
    def to_dict(self) -> dict:
        d = asdict(self)
        # Remove None values for cleaner output
        return {k: v for k, v in d.items() if v is not None}


class ExperimentTracker:
    """Tracks and compiles quantum experiments from all sources."""
    
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root)
        self.experiments: List[QuantumExperiment] = []
        
    def extract_github_workflows(self) -> List[QuantumExperiment]:
        """Extract experiment data from GitHub Actions workflow runs."""
        experiments = []
        
        try:
            # Get workflow runs via gh CLI
            result = subprocess.run(
                ["gh", "run", "list", "--workflow=heartbeat.yml", "--limit", "100",
                 "--json", "databaseId,status,conclusion,createdAt"],
                capture_output=True, text=True, cwd=self.root
            )
            
            if result.returncode != 0:
                print(f"GitHub CLI error: {result.stderr}")
                return []
            
            runs = json.loads(result.stdout)
            
            for run in runs:
                exp = QuantumExperiment(
                    id=f"gh_{run['databaseId']}",
                    source="github",
                    experiment_type="heartbeat",
                    backend="simulator",  # Default, may be overwritten
                    timestamp=run['createdAt'],
                    status=run['conclusion'] or run['status'],
                    num_qubits=27,  # Default heartbeat qubits
                    shots=1024,
                )
                
                # Map status to coherence (rough approximation)
                if exp.status == "success":
                    exp.coherence = 0.85  # Placeholder
                    exp.fidelity = 0.95
                else:
                    exp.coherence = 0.0
                    exp.fidelity = 0.0
                
                experiments.append(exp)
                
        except Exception as e:
            print(f"Error extracting GitHub workflows: {e}")
        
        return experiments
    
    def extract_ibm_quantum_jobs(self) -> List[QuantumExperiment]:
        """Extract experiment data from IBM Quantum job history."""
        experiments = []
        
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            
            token = os.getenv("IBM_QUANTUM_TOKEN")
            if not token:
                print("IBM_QUANTUM_TOKEN not set")
                return []
            
            service = QiskitRuntimeService(
                channel="ibm_quantum_platform", 
                token=token
            )
            
            jobs = service.jobs(limit=100)
            
            for job in jobs:
                # Determine experiment type from job tags or circuit name
                exp_type = "unknown"
                if hasattr(job, 'tags') and job.tags:
                    if 'heartbeat' in str(job.tags):
                        exp_type = "heartbeat"
                    elif 'pi' in str(job.tags):
                        exp_type = "pi_pulse"
                
                # Try to get circuit info
                num_qubits = 0
                try:
                    # This might not always work
                    inputs = job.inputs
                    if inputs and 'circuits' in inputs:
                        num_qubits = inputs['circuits'][0].num_qubits
                except:
                    pass
                
                exp = QuantumExperiment(
                    id=f"ibm_{job.job_id()}",
                    source="ibm_quantum",
                    experiment_type=exp_type,
                    backend=str(job.backend()).replace("<IBMBackend('", "").replace("')>", ""),
                    timestamp=str(job.creation_date)[:19],
                    status=str(job.status()),
                    num_qubits=num_qubits,
                )
                
                # If job is done, try to extract metrics
                if exp.status == "DONE":
                    try:
                        result = job.result()
                        # Extract counts from first pub result
                        if result and len(result) > 0:
                            pub_result = result[0]
                            data = pub_result.data
                            
                            # Try to get counts
                            for attr in ['meas', 'result', 'c']:
                                if hasattr(data, attr):
                                    counts_array = getattr(data, attr)
                                    counts = counts_array.get_counts()
                                    exp.counts = counts
                                    exp.shots = sum(counts.values())
                                    
                                    # Calculate coherence from counts
                                    probs = [c/exp.shots for c in counts.values()]
                                    import math
                                    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
                                    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1
                                    exp.coherence = 1 - (entropy / max_entropy) if max_entropy > 0 else 1
                                    exp.entropy = entropy
                                    break
                    except Exception as e:
                        pass  # Can't get result details
                
                experiments.append(exp)
                
        except Exception as e:
            print(f"Error extracting IBM Quantum jobs: {e}")
        
        return experiments
    
    def extract_local_files(self) -> List[QuantumExperiment]:
        """Extract experiment data from local result files."""
        experiments = []
        
        # Scan directories
        result_dirs = [
            self.root / "cardiogram_results",
            self.root / "quantum_jobs" / "results",
            self.root / "heartbeat_data",
            self.root / "examples" / "results",
        ]
        
        for result_dir in result_dirs:
            if not result_dir.exists():
                continue
            
            for json_file in result_dir.glob("**/*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Determine experiment type from filename or content
                    filename = json_file.stem.lower()
                    if "cardiogram" in filename or "beat_number" in data:
                        exp_type = "cardiogram"
                    elif "pi_pulse" in filename or "estimated_pi" in data:
                        exp_type = "pi_pulse"
                    elif "consciousness" in filename:
                        exp_type = "consciousness"
                    elif "heartbeat" in filename:
                        exp_type = "heartbeat"
                    else:
                        exp_type = "unknown"
                    
                    exp = QuantumExperiment(
                        id=f"local_{json_file.stem}",
                        source="local",
                        experiment_type=exp_type,
                        backend=data.get('backend', 'unknown'),
                        timestamp=data.get('timestamp', str(datetime.now())),
                        status="success",
                        num_qubits=data.get('num_qubits', data.get('total_qubits', 0)),
                        circuit_depth=data.get('circuit_depth', 0),
                        shots=data.get('shots', data.get('n_shots', 0)),
                        coherence=data.get('coherence', 0.0),
                        entropy=data.get('entropy', 0.0),
                        fidelity=data.get('overall_fidelity', data.get('fidelity', 0.0)),
                        error_rate=data.get('overall_error', data.get('error_rate', 0.0)),
                        counts=data.get('counts'),
                        raw_file=str(json_file),
                    )
                    
                    # Extract hypersphere coords if present
                    if 'hypersphere' in data:
                        hs = data['hypersphere']
                        exp.theta = hs.get('theta', 0)
                        exp.phi = hs.get('phi', 0)
                        exp.radius = hs.get('radius', 1)
                        exp.hue = hs.get('hue', 0.5)
                    
                    experiments.append(exp)
                    
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
        
        return experiments
    
    def compute_hypersphere_coordinates(self, exp: QuantumExperiment) -> None:
        """Compute hypersphere coordinates for visualization."""
        import math
        
        # Theta (polar): based on experiment type
        type_theta = {
            'heartbeat': 0.3,      # North
            'cardiogram': 0.4,     # North-ish
            'consciousness': 0.5,  # Equator
            'pi_pulse': 0.7,       # South-ish
            'entanglement': 0.6,   # Mid-south
            'unknown': 0.5,        # Equator
        }
        base_theta = type_theta.get(exp.experiment_type, 0.5) * math.pi
        
        # Modify theta by coherence (high coherence = toward equator)
        exp.theta = base_theta * (1 - 0.3 * exp.coherence)
        
        # Phi (azimuthal): based on timestamp
        if exp.timestamp:
            try:
                dt = datetime.fromisoformat(exp.timestamp.replace('Z', '+00:00'))
                # Map time of day to angle
                hour_angle = (dt.hour + dt.minute/60) / 24 * 2 * math.pi
                exp.phi = hour_angle
            except:
                exp.phi = 0
        
        # Radius: based on fidelity/coherence
        exp.radius = 0.5 + 0.5 * max(exp.coherence, exp.fidelity)
        
        # Hue: based on backend
        backend_hue = {
            'ibm_torino': 0.55,    # Cyan
            'ibm_fez': 0.7,        # Blue
            'ibm_marrakesh': 0.8,  # Purple
            'simulator': 0.3,      # Green
            'unknown': 0.0,        # Red
        }
        exp.hue = backend_hue.get(exp.backend, 0.5)
    
    def compile_all(self) -> Dict[str, Any]:
        """Compile all experiment data from all sources."""
        print("=" * 60)
        print("QUANTUM EXPERIMENT TRACKER")
        print("=" * 60)
        print()
        
        # Extract from all sources
        print("📡 Extracting from GitHub Actions...")
        github_exps = self.extract_github_workflows()
        print(f"   Found: {len(github_exps)} workflow runs")
        
        print("🌐 Extracting from IBM Quantum...")
        ibm_exps = self.extract_ibm_quantum_jobs()
        print(f"   Found: {len(ibm_exps)} jobs")
        
        print("📁 Extracting from local files...")
        local_exps = self.extract_local_files()
        print(f"   Found: {len(local_exps)} result files")
        
        # Combine all
        self.experiments = github_exps + ibm_exps + local_exps
        
        # Compute hypersphere coordinates
        print("\n🌐 Computing hypersphere coordinates...")
        for exp in self.experiments:
            self.compute_hypersphere_coordinates(exp)
        
        # Statistics
        print("\n📊 Summary:")
        
        by_source = defaultdict(int)
        by_type = defaultdict(int)
        by_backend = defaultdict(int)
        by_status = defaultdict(int)
        
        for exp in self.experiments:
            by_source[exp.source] += 1
            by_type[exp.experiment_type] += 1
            by_backend[exp.backend] += 1
            by_status[exp.status] += 1
        
        print(f"\n   By Source:")
        for k, v in sorted(by_source.items()):
            print(f"      {k}: {v}")
        
        print(f"\n   By Type:")
        for k, v in sorted(by_type.items()):
            print(f"      {k}: {v}")
        
        print(f"\n   By Backend:")
        for k, v in sorted(by_backend.items()):
            print(f"      {k}: {v}")
        
        print(f"\n   By Status:")
        for k, v in sorted(by_status.items()):
            print(f"      {k}: {v}")
        
        # Prepare output
        output = {
            "compiled_at": datetime.now().isoformat(),
            "total_experiments": len(self.experiments),
            "summary": {
                "by_source": dict(by_source),
                "by_type": dict(by_type),
                "by_backend": dict(by_backend),
                "by_status": dict(by_status),
            },
            "experiments": [exp.to_dict() for exp in self.experiments],
        }
        
        return output
    
    def export_for_visualization(self, output_path: str = None) -> str:
        """Export data in format optimized for hypersphere visualization."""
        
        if output_path is None:
            output_path = self.root / "web" / "public" / "quantum_experiments.json"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Compile data
        data = self.compile_all()
        
        # Add visualization-specific format
        viz_points = []
        for exp in self.experiments:
            point = {
                "id": exp.id,
                "type": exp.experiment_type,
                "backend": exp.backend,
                "timestamp": exp.timestamp,
                
                # Spherical coordinates
                "theta": exp.theta,
                "phi": exp.phi,
                "r": exp.radius,
                
                # Visual properties
                "hue": exp.hue,
                "saturation": 0.8 if exp.status == "success" else 0.3,
                "lightness": 0.3 + 0.4 * exp.coherence,
                "size": 0.01 + 0.02 * exp.coherence,
                
                # Metrics
                "coherence": exp.coherence,
                "fidelity": exp.fidelity,
                "entropy": exp.entropy,
            }
            viz_points.append(point)
        
        data["visualization_points"] = viz_points
        
        # Save
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Exported to: {output_path}")
        print(f"   Total points: {len(viz_points)}")
        
        return str(output_path)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Track and compile quantum experiments")
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--root', '-r', default='.', help='Workspace root')
    
    args = parser.parse_args()
    
    tracker = ExperimentTracker(args.root)
    output_path = tracker.export_for_visualization(args.output)
    
    print("\n" + "=" * 60)
    print("✅ COMPILATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
