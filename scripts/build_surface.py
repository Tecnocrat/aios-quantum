#!/usr/bin/env python3
"""
Hypersphere Surface Builder - Combine All Quantum Data

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Build complete hypersphere surface from all heartbeat/cardiogram data
"""

import os
import sys
import json
import glob
import math
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum.supercell.hypersphere import HypersphereSurface


def load_cardiogram_data(results_dir: str) -> list:
    """Load all cardiogram JSON files."""
    data = []
    for filepath in glob.glob(os.path.join(results_dir, "cardiogram_real_*.json")):
        with open(filepath) as f:
            d = json.load(f)
            d["source_file"] = os.path.basename(filepath)
            data.append(d)
    return sorted(data, key=lambda x: x.get("timestamp", ""))


def load_heartbeat_data(results_dir: str) -> list:
    """Load real heartbeat data and extract error information."""
    data = []
    for filepath in glob.glob(os.path.join(results_dir, "real_beat_*.json")):
        with open(filepath) as f:
            d = json.load(f)
            # Convert heartbeat format to cardiogram format
            counts = d.get("counts", {})
            total = sum(counts.values())
            num_qubits = d.get("num_qubits", 5)
            
            # Expected state for heartbeat (superposition collapse)
            # This is different - heartbeat is H gates, not X gates
            # All 32 states should be roughly equal, so "error" = deviation from uniform
            expected_per_state = total / (2 ** num_qubits)
            
            # For heartbeat, calculate per-qubit bias as "error"
            qubit_errors = []
            for q in range(num_qubits):
                ones_count = 0
                for state, count in counts.items():
                    if len(state) > q and state[-(q+1)] == "1":
                        ones_count += count
                # Deviation from 50% is the "error" (bias)
                bias = abs(0.5 - (ones_count / total))
                qubit_errors.append(bias)
            
            data.append({
                "timestamp": d.get("timestamp_utc", ""),
                "backend": d.get("backend", "unknown"),
                "job_id": d.get("job_id", ""),
                "qubit_errors": qubit_errors,
                "num_qubits": num_qubits,
                "source_file": os.path.basename(filepath),
                "type": "heartbeat"
            })
    return data


def build_combined_surface(cardiograms: list, heartbeats: list) -> dict:
    """Build a hypersphere surface from all quantum data."""
    surface = HypersphereSurface()
    
    all_data = []
    
    # Add cardiograms
    for i, card in enumerate(cardiograms):
        all_data.append({
            "beat": i,
            "qubit_errors": card.get("qubit_errors", [0]*5),
            "timestamp": card.get("timestamp", ""),
            "backend": card.get("backend", ""),
            "type": "cardiogram",
            "source": card.get("source_file", "")
        })
    
    # Add heartbeats
    offset = len(cardiograms)
    for i, hb in enumerate(heartbeats):
        all_data.append({
            "beat": offset + i,
            "qubit_errors": hb.get("qubit_errors", [0]*5),
            "timestamp": hb.get("timestamp", ""),
            "backend": hb.get("backend", ""),
            "type": "heartbeat",
            "source": hb.get("source_file", "")
        })
    
    # Build surface - each beat becomes a ring at different phi
    total_beats = len(all_data)
    for i, data in enumerate(all_data):
        phi_position = (i / max(total_beats, 1))  # Spread across 0-1 (one hemisphere)
        surface.add_multi_qubit_point(
            qubit_errors=data["qubit_errors"],
            beat_number=data["beat"],
            time_position=phi_position,
        )
    
    mesh = surface.to_mesh_data()
    mesh["source_data"] = all_data
    
    return mesh


def generate_ascii_visualization(surface_data: dict) -> str:
    """Generate ASCII art visualization of the surface."""
    vertices = surface_data.get("vertices", [])
    if not vertices:
        return "No vertices to display"
    
    # Group by beat (time position)
    beats = {}
    for v in vertices:
        beat = v["quantum"]["beat"]
        if beat not in beats:
            beats[beat] = []
        beats[beat].append(v)
    
    lines = []
    lines.append("=" * 70)
    lines.append("  HYPERSPHERE SURFACE - QUANTUM ERROR TOPOLOGY")
    lines.append("=" * 70)
    lines.append("")
    lines.append("  Height Scale: ▼ valley (low error) ─── ▲ mountain (high error)")
    lines.append("  Range: -1.0 (perfect) to +1.0 (high error)")
    lines.append("")
    
    for beat_num in sorted(beats.keys()):
        beat_vertices = beats[beat_num]
        source = surface_data.get("source_data", [{}])[beat_num] if beat_num < len(surface_data.get("source_data", [])) else {}
        
        lines.append(f"  Beat {beat_num} [{source.get('type', 'unknown')}] - {source.get('backend', 'unknown')}")
        lines.append("  " + "-" * 50)
        
        # Sort by theta (qubit position)
        beat_vertices.sort(key=lambda v: v["spherical"]["theta"])
        
        for i, v in enumerate(beat_vertices):
            height = v["height"]
            error = v["quantum"]["error"]
            
            # Create visual bar
            bar_pos = int((height + 1) * 25)  # 0-50 range
            bar = " " * bar_pos + "█" + " " * (50 - bar_pos)
            
            # Arrow indicator
            if height < -0.5:
                indicator = "▼"
            elif height > 0.5:
                indicator = "▲"
            else:
                indicator = "─"
            
            lines.append(f"    Q{i}: [{bar}] {height:+.3f} {indicator} ({error:.2%})")
        
        lines.append("")
    
    # Summary statistics
    heights = surface_data.get("heights", [])
    if heights:
        lines.append("  " + "=" * 50)
        lines.append("  SURFACE STATISTICS")
        lines.append("  " + "-" * 50)
        lines.append(f"    Total vertices: {len(vertices)}")
        lines.append(f"    Total beats: {len(beats)}")
        lines.append(f"    Mean height: {sum(heights)/len(heights):+.4f}")
        lines.append(f"    Height range: [{min(heights):+.3f}, {max(heights):+.3f}]")
        variance = sum((h - sum(heights)/len(heights))**2 for h in heights) / len(heights)
        lines.append(f"    Surface roughness: {variance:.6f}")
    
    return "\n".join(lines)


def generate_3d_coords_display(surface_data: dict) -> str:
    """Generate 3D coordinate listing for engine consumption."""
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("  3D VERTEX COORDINATES (for hypersphere projection)")
    lines.append("=" * 70)
    lines.append("")
    lines.append("  Format: (x, y, z) on displaced unit sphere")
    lines.append("")
    
    vertices = surface_data.get("vertices", [])
    for i, v in enumerate(vertices):
        cart = v["cartesian"]
        sph = v["spherical"]
        lines.append(f"  V{i:02d}: ({cart['x']:+.4f}, {cart['y']:+.4f}, {cart['z']:+.4f})")
        lines.append(f"        θ={sph['theta']:.3f}, φ={sph['phi']:.3f}, h={v['height']:+.3f}")
    
    return "\n".join(lines)


def main():
    print("Loading quantum data...")
    
    cardiograms = load_cardiogram_data("cardiogram_results")
    heartbeats = load_heartbeat_data("heartbeat_results")
    
    print(f"Found {len(cardiograms)} cardiograms")
    print(f"Found {len(heartbeats)} real heartbeats")
    
    print("\nBuilding hypersphere surface...")
    surface = build_combined_surface(cardiograms, heartbeats)
    
    # Display visualization
    print(generate_ascii_visualization(surface))
    print(generate_3d_coords_display(surface))
    
    # Save combined surface
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = f"cardiogram_results/hypersphere_surface_{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump(surface, f, indent=2)
    
    print()
    print(f"Combined surface saved: {output_path}")
    print(f"Total vertices: {surface['vertex_count']}")
    print(f"Total beats: {surface['total_beats']}")
    print()
    print("The quantum error noise is now encoded in the hypersphere topology.")


if __name__ == "__main__":
    main()
