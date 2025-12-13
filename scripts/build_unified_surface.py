#!/usr/bin/env python3
"""
UNIFIED HYPERSPHERE SURFACE BUILDER
===================================

Builds a complete hypersphere surface from ALL quantum experiments:
- Heartbeats (consciousness probes)
- Cardiograms (circuit analysis)
- Exotic experiments (π search, arithmetic, entanglement, golden ratio, random)

Uses the ExperimentRegistry for unified classification and the
experiment taxonomy for geometric organization.

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-13
  purpose: Unified surface from all quantum data with exotic experiments
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aios_quantum.engine.experiment_registry import (
    ExperimentRegistry,
    UnifiedExperiment,
    build_unified_surface,
)
from aios_quantum.engine.experiment_taxonomy import (
    ExperimentClass,
    ExperimentOrigin,
)
from aios_quantum.supercell.hypersphere import HypersphereSurface


def run_exotic_experiments() -> list:
    """Run exotic experiments and return results."""
    print("\n🔬 Running exotic quantum experiments...")
    
    try:
        from aios_quantum.circuits.exotic_experiments import (
            run_exotic_experiment,
            ExoticResult,
        )
        
        experiments = [
            ("pi_search", 4, "Searching for π digits in superposition"),
            ("arithmetic", 4, "Quantum addition in superposition"),
            ("entanglement", 4, "Entanglement witness measurement"),
            ("golden_ratio", 5, "Golden ratio (φ) circuit"),
            ("random", 8, "Quantum random number generation"),
            ("bell", 2, "Bell state (|Φ+⟩)"),
            ("ghz", 3, "GHZ entangled state"),
        ]
        
        results = []
        for exp_type, n_qubits, description in experiments:
            print(f"  • {description}...", end=" ")
            result = run_exotic_experiment(exp_type, n_qubits, n_shots=1024)
            results.append(result)
            print(f"✓ (coherence: {result.coherence:.3f})")
        
        return results
        
    except ImportError as e:
        print(f"  ⚠ Exotic experiments unavailable: {e}")
        return []


def save_exotic_results(results: list, output_dir: str) -> None:
    """Save exotic experiment results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for result in results:
        filepath = output_path / f"{result.experiment_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"  Saved: {filepath.name}")


def build_unified_hypersphere(
    registry: ExperimentRegistry,
    include_exotic: bool = True,
) -> dict:
    """Build hypersphere surface from registry data.
    
    Combines the legacy HypersphereSurface geometry with the
    new unified experiment coordinates.
    """
    surface = HypersphereSurface()
    
    # Get all experiments sorted by class
    experiments = list(registry.experiments.values())
    
    # Build vertices from experiments
    vertices = []
    for i, exp in enumerate(experiments):
        # Get 3D position from experiment coordinates
        x, y, z = exp.position_3d
        
        # Scale to unit sphere with some offset for depth
        r = 0.9 + 0.1 * (1 - exp.depth / (exp.depth + 1))
        
        # Create vertex data
        vertex = {
            "id": exp.experiment_id,
            "position": [x * r, y * r, z * r],
            "color": list(exp.color),
            "spherical": {
                "theta": exp.theta,
                "phi": exp.phi,
                "depth": exp.depth,
            },
            "metadata": {
                "class": exp.metadata.experiment_class.value,
                "origin": exp.metadata.origin.value,
                "timestamp": exp.metadata.timestamp,
                "backend": exp.metadata.backend,
                "coherence": exp.metadata.coherence,
                "entropy": exp.metadata.entropy,
                "n_qubits": exp.metadata.n_qubits,
            },
            "connections": exp.connected_experiments,
        }
        vertices.append(vertex)
    
    # Build edges from connections
    edges = []
    seen_edges = set()
    for exp in experiments:
        for connected_id in exp.connected_experiments:
            edge_key = tuple(sorted([exp.experiment_id, connected_id]))
            if edge_key not in seen_edges and connected_id in registry.experiments:
                seen_edges.add(edge_key)
                # Get positions for edge
                other = registry.experiments[connected_id]
                edges.append({
                    "from": exp.experiment_id,
                    "to": connected_id,
                    "from_pos": list(exp.position_3d),
                    "to_pos": list(other.position_3d),
                    "type": "relation",
                })
    
    # Statistics by class
    stats = registry.get_statistics()
    
    return {
        "vertices": vertices,
        "edges": edges,
        "statistics": stats,
        "generated_at": datetime.now().isoformat(),
        "version": "2.0-unified",
        "vertex_count": len(vertices),
        "edge_count": len(edges),
    }


def generate_class_distribution_display(stats: dict) -> str:
    """Generate visual display of experiment class distribution."""
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("  EXPERIMENT CLASS DISTRIBUTION")
    lines.append("=" * 70)
    lines.append("")
    
    by_class = stats.get("by_class", {})
    total = stats.get("total", 1)
    
    # Sort by count
    sorted_classes = sorted(by_class.items(), key=lambda x: -x[1])
    
    for class_name, count in sorted_classes:
        pct = count / total * 100
        bar_len = int(pct / 2)
        bar = "█" * bar_len
        
        # Color coding by class
        if class_name in ["heartbeat", "cardiogram"]:
            icon = "💓"
        elif class_name in ["arithmetic", "search", "factoring"]:
            icon = "🔢"
        elif class_name in ["entanglement", "teleportation", "witness"]:
            icon = "🔮"
        elif class_name in ["pi_search", "golden", "random"]:
            icon = "✨"
        else:
            icon = "📊"
        
        lines.append(f"  {icon} {class_name:15} {bar:25} {count:3} ({pct:5.1f}%)")
    
    lines.append("")
    lines.append(f"  Total experiments: {total}")
    lines.append("")
    
    by_origin = stats.get("by_origin", {})
    lines.append("  By origin:")
    for origin, count in sorted(by_origin.items()):
        icon = "🔵" if origin == "ibm_quantum" else "⚪"
        lines.append(f"    {icon} {origin}: {count}")
    
    return "\n".join(lines)


def generate_topology_map(surface_data: dict) -> str:
    """Generate ASCII topology map of the hypersphere."""
    vertices = surface_data.get("vertices", [])
    
    if not vertices:
        return "No vertices to display"
    
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("  HYPERSPHERE TOPOLOGY MAP")
    lines.append("=" * 70)
    lines.append("")
    lines.append("  θ = 0 (North Pole): Consciousness (heartbeats)")
    lines.append("  θ = π/2 (Equator): Computation (arithmetic, search)")
    lines.append("  θ = π (South Pole): Constants & Chaos (π, φ, random)")
    lines.append("")
    
    # Create a 2D projection map (theta vs phi)
    # Map theta (0, π) to rows (0, 15)
    # Map phi (0, 2π) to cols (0, 59)
    map_height = 16
    map_width = 60
    map_grid = [[' ' for _ in range(map_width)] for _ in range(map_height)]
    
    # Place vertices
    for v in vertices:
        theta = v["spherical"]["theta"]
        phi = v["spherical"]["phi"]
        
        row = min(map_height - 1, int(theta / 3.14159 * (map_height - 1)))
        col = min(map_width - 1, int(phi / (2 * 3.14159) * (map_width - 1)))
        
        # Character based on class
        exp_class = v["metadata"]["class"]
        if exp_class in ["heartbeat", "cardiogram"]:
            char = "♥"
        elif exp_class in ["arithmetic", "search"]:
            char = "+"
        elif exp_class in ["entanglement", "teleportation"]:
            char = "⊗"
        elif exp_class == "pi_search":
            char = "π"
        elif exp_class == "golden_ratio":
            char = "φ"
        elif exp_class == "random":
            char = "?"
        else:
            char = "·"
        
        map_grid[row][col] = char
    
    # Draw map with frame
    lines.append("  ┌" + "─" * map_width + "┐")
    for row in range(map_height):
        line = "".join(map_grid[row])
        lines.append(f"  │{line}│")
    lines.append("  └" + "─" * map_width + "┘")
    lines.append("  0                            φ                           2π")
    
    # Legend
    lines.append("")
    lines.append("  Legend: ♥=heartbeat  +=arithmetic  ⊗=entanglement  π=pi  φ=golden  ?=random")
    
    return "\n".join(lines)


def main():
    print("=" * 70)
    print("  UNIFIED HYPERSPHERE SURFACE BUILDER")
    print("=" * 70)
    print()
    
    # Initialize registry
    base_path = Path(__file__).parent.parent
    registry = ExperimentRegistry(str(base_path))
    
    # Load all existing experiments
    print("📂 Loading quantum experiments from all sources...")
    count = registry.load_all()
    print(f"   Loaded {count} experiments")
    
    # Run exotic experiments
    exotic_results = run_exotic_experiments()
    
    # Save exotic results
    if exotic_results:
        print("\n💾 Saving exotic experiment results...")
        exotic_dir = base_path / "examples" / "results" / "exotic"
        save_exotic_results(exotic_results, str(exotic_dir))
        
        # Add exotic results to registry
        print("\n📊 Adding exotic experiments to registry...")
        for result in exotic_results:
            exp_class_map = {
                "pi_search": ExperimentClass.PI_SEARCH,
                "arithmetic": ExperimentClass.ARITHMETIC,
                "entanglement": ExperimentClass.ENTANGLEMENT,
                "golden_ratio": ExperimentClass.GOLDEN,
                "random": ExperimentClass.RANDOM,
                "bell": ExperimentClass.ENTANGLEMENT,
                "ghz": ExperimentClass.ENTANGLEMENT,
            }
            exp_class = exp_class_map.get(result.experiment_type, ExperimentClass.WITNESS)
            registry.add_experiment(result.to_dict(), exp_class, ExperimentOrigin.SIMULATOR)
        
        print(f"   Registry now has {len(registry.experiments)} experiments")
    
    # Build unified surface
    print("\n🌐 Building unified hypersphere surface...")
    surface = build_unified_hypersphere(registry)
    
    # Display statistics
    print(generate_class_distribution_display(surface["statistics"]))
    
    # Display topology map
    print(generate_topology_map(surface))
    
    # Save surface for web visualization
    output_dir = base_path / "web" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "unified_surface.json"
    with open(output_path, 'w') as f:
        json.dump(surface, f, indent=2)
    print(f"\n✅ Surface saved: {output_path}")
    
    # Also save to cardiogram_results for backup
    backup_path = base_path / "cardiogram_results" / f"unified_surface_{datetime.now().strftime('%Y%m%d')}.json"
    with open(backup_path, 'w') as f:
        json.dump(surface, f, indent=2)
    print(f"✅ Backup saved: {backup_path}")
    
    print()
    print(f"🎯 Total vertices: {surface['vertex_count']}")
    print(f"🔗 Total edges: {surface['edge_count']}")
    print()
    print("The unified quantum experiment topology is ready for visualization.")
    print("Start the web server with: cd web && npm run dev")
    print("View at: http://localhost:3000/hypersphere/")


if __name__ == "__main__":
    main()
