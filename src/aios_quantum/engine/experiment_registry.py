"""
EXPERIMENT REGISTRY
===================

Central registry for all quantum experiments.
Loads, classifies, and organizes experiments from multiple sources
for unified visualization on the hypersphere surface.

Data Sources:
- cardiogram_results/      → Real quantum cardiograms
- heartbeat_data/          → Real quantum heartbeats
- heartbeat_data/daily/    → Simulator daily beats
- examples/results/        → Ad-hoc experiment results
- cloud (Cloudant)         → Synced cloud data

Each experiment is classified by type and assigned:
- Geometric coordinates (where on the hypersphere)
- Color encoding (visual identification)
- Relational links (connections to other experiments)
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Iterator, Tuple
from datetime import datetime
import math

from .experiment_taxonomy import (
    ExperimentClass,
    ExperimentOrigin,
    ExperimentMetadata,
    GeometricSignature,
    ColorFamily,
    classify_experiment,
    EXPERIMENT_SIGNATURES,
    EXPERIMENT_COLORS,
)


@dataclass
class UnifiedExperiment:
    """A single experiment with full classification and coordinates."""
    
    # Identity
    experiment_id: str
    metadata: ExperimentMetadata
    
    # Raw data
    raw_data: Dict[str, Any]
    counts: Dict[str, int] = field(default_factory=dict)
    
    # Computed coordinates (assigned by registry)
    theta: float = 0.0      # Polar angle [0, π]
    phi: float = 0.0        # Azimuthal angle [0, 2π]
    depth: float = 1.0      # Hypersphere depth
    
    # Computed color
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    
    # Relations
    connected_experiments: List[str] = field(default_factory=list)
    
    @property
    def position_3d(self) -> Tuple[float, float, float]:
        """Convert spherical coordinates to 3D Cartesian."""
        r = 1.0 - (self.depth / (self.depth + 1))  # Map depth to [0, 1]
        x = r * math.sin(self.theta) * math.cos(self.phi)
        y = r * math.sin(self.theta) * math.sin(self.phi)
        z = r * math.cos(self.theta)
        return (x, y, z)
    
    def to_surface_dict(self) -> Dict[str, Any]:
        """Export as surface vertex for visualization."""
        x, y, z = self.position_3d
        return {
            "id": self.experiment_id,
            "position": [x, y, z],
            "color": list(self.color),
            "metadata": {
                "class": self.metadata.experiment_class.value,
                "origin": self.metadata.origin.value,
                "timestamp": self.metadata.timestamp,
                "backend": self.metadata.backend,
                "coherence": self.metadata.coherence,
                "entropy": self.metadata.entropy,
                "n_qubits": self.metadata.n_qubits,
                "dominant_state": self.metadata.dominant_state,
            },
            "connections": self.connected_experiments,
        }


class ExperimentRegistry:
    """
    Central registry for all quantum experiments.
    
    Responsibilities:
    1. Load experiments from all sources
    2. Classify by type (heartbeat, arithmetic, etc.)
    3. Assign geometric coordinates based on type
    4. Build relational graph between experiments
    5. Export unified surface for visualization
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.experiments: Dict[str, UnifiedExperiment] = {}
        self._position_counters: Dict[ExperimentClass, int] = {}
    
    def load_all(self) -> int:
        """Load all experiments from all sources.
        
        Returns number of experiments loaded.
        """
        count = 0
        
        # Load cardiograms (real quantum)
        count += self._load_from_directory(
            self.base_path / "cardiogram_results",
            ExperimentOrigin.IBM_QUANTUM,
            ExperimentClass.CARDIOGRAM,
        )
        
        # Load heartbeats (real quantum)
        count += self._load_from_directory(
            self.base_path / "heartbeat_data",
            ExperimentOrigin.IBM_QUANTUM,
            ExperimentClass.HEARTBEAT,
            recursive=False,
        )
        
        # Load daily beats (simulator)
        count += self._load_from_directory(
            self.base_path / "heartbeat_data" / "daily",
            ExperimentOrigin.SIMULATOR,
            ExperimentClass.HEARTBEAT,
        )
        
        # Load ad-hoc results
        count += self._load_from_directory(
            self.base_path / "examples" / "results",
            ExperimentOrigin.LOCAL,
            None,  # Auto-classify
        )
        
        # Build relations after all loaded
        self._build_relations()
        
        return count
    
    def _load_from_directory(
        self,
        directory: Path,
        origin: ExperimentOrigin,
        default_class: Optional[ExperimentClass],
        recursive: bool = True,
    ) -> int:
        """Load experiments from a directory."""
        if not directory.exists():
            return 0
        
        count = 0
        pattern = "**/*.json" if recursive else "*.json"
        
        for json_file in directory.glob(pattern):
            try:
                experiment = self._load_experiment_file(
                    json_file, origin, default_class
                )
                if experiment:
                    self.experiments[experiment.experiment_id] = experiment
                    count += 1
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")
        
        return count
    
    def _load_experiment_file(
        self,
        filepath: Path,
        origin: ExperimentOrigin,
        default_class: Optional[ExperimentClass],
    ) -> Optional[UnifiedExperiment]:
        """Load a single experiment from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Auto-classify if no default
        exp_class = default_class or classify_experiment(data)
        
        # Extract ID
        exp_id = data.get("id", data.get("experiment_id", filepath.stem))
        
        # Extract timestamp
        timestamp = data.get("timestamp", data.get("created_at", ""))
        if not timestamp:
            # Try to extract from filename
            timestamp = filepath.stem
        
        # Extract backend
        backend = data.get("backend", data.get("backend_name", "unknown"))
        if backend == "unknown" and "simulator" in str(filepath).lower():
            backend = "simulator"
        
        # Determine origin from backend if IBM
        if "ibm_" in backend.lower():
            origin = ExperimentOrigin.IBM_QUANTUM
        elif "simulator" in backend.lower() or "statevector" in backend.lower():
            origin = ExperimentOrigin.SIMULATOR
        
        # Extract quantum properties
        n_qubits = data.get("n_qubits", data.get("num_qubits", 0))
        n_shots = data.get("shots", data.get("n_shots", 0))
        depth = data.get("circuit_depth", data.get("depth", 0))
        
        # Extract results
        counts = data.get("counts", data.get("measurement_counts", {}))
        coherence = data.get("coherence", 0.0)
        entropy = data.get("entropy", 0.0)
        error_rate = data.get("error_rate", 0.0)
        
        # Find dominant state
        dominant_state = ""
        if counts:
            dominant_state = max(counts, key=lambda k: counts[k])
        
        # Create metadata
        metadata = ExperimentMetadata(
            experiment_class=exp_class,
            origin=origin,
            experiment_id=exp_id,
            timestamp=timestamp,
            backend=backend,
            n_qubits=n_qubits,
            n_shots=n_shots,
            depth=depth,
            dominant_state=dominant_state,
            coherence=coherence,
            entropy=entropy,
            error_rate=error_rate,
        )
        
        # Assign coordinates
        theta, phi, hyperdepth = self._assign_coordinates(exp_class, metadata)
        
        # Assign color
        color = self._assign_color(exp_class, coherence, entropy)
        
        return UnifiedExperiment(
            experiment_id=exp_id,
            metadata=metadata,
            raw_data=data,
            counts=counts,
            theta=theta,
            phi=phi,
            depth=hyperdepth,
            color=color,
        )
    
    def _assign_coordinates(
        self,
        exp_class: ExperimentClass,
        metadata: ExperimentMetadata,
    ) -> Tuple[float, float, float]:
        """Assign hypersphere coordinates based on experiment type."""
        signature = EXPERIMENT_SIGNATURES.get(
            exp_class,
            EXPERIMENT_SIGNATURES[ExperimentClass.HEARTBEAT]
        )
        
        # Get position counter for this class
        counter = self._position_counters.get(exp_class, 0)
        self._position_counters[exp_class] = counter + 1
        
        # Calculate t parameter based on counter
        # Use golden ratio for nice distribution
        golden = (1 + math.sqrt(5)) / 2
        t = (counter * golden) % 1.0
        
        # Get base position from signature
        theta, phi, depth = signature.sample_position(t)
        
        # Add variation based on coherence
        if metadata.coherence > 0:
            theta += 0.05 * (metadata.coherence - 0.5)
        
        # Depth varies with entropy
        depth *= (1 + 0.3 * metadata.entropy)
        
        return (theta, phi, depth)
    
    def _assign_color(
        self,
        exp_class: ExperimentClass,
        coherence: float,
        entropy: float,
    ) -> Tuple[float, float, float, float]:
        """Assign color based on experiment type and results."""
        color_family = EXPERIMENT_COLORS.get(
            exp_class,
            EXPERIMENT_COLORS[ExperimentClass.HEARTBEAT]
        )
        
        # Value is coherence, certainty is inverse of entropy
        value = coherence
        certainty = max(0.1, 1.0 - entropy / 5.0)  # Normalize entropy
        
        return color_family.encode(value, certainty)
    
    def _build_relations(self):
        """Build relational connections between experiments."""
        # Group by class
        by_class: Dict[ExperimentClass, List[UnifiedExperiment]] = {}
        for exp in self.experiments.values():
            exp_class = exp.metadata.experiment_class
            if exp_class not in by_class:
                by_class[exp_class] = []
            by_class[exp_class].append(exp)
        
        # Apply relational rules
        for exp in self.experiments.values():
            relations = exp.metadata.relations
            
            # Connect to related classes
            for related_class in relations.connects_to:
                if related_class in by_class:
                    # Connect to nearest experiment of that class
                    nearest = self._find_nearest(exp, by_class[related_class])
                    if nearest:
                        exp.connected_experiments.append(nearest.experiment_id)
            
            # Cluster with similar classes
            for cluster_class in relations.cluster_with:
                if cluster_class in by_class:
                    # Connect to all in cluster (limited to 3)
                    for other in by_class[cluster_class][:3]:
                        if other.experiment_id not in exp.connected_experiments:
                            exp.connected_experiments.append(other.experiment_id)
    
    def _find_nearest(
        self,
        exp: UnifiedExperiment,
        candidates: List[UnifiedExperiment],
    ) -> Optional[UnifiedExperiment]:
        """Find nearest experiment by spherical distance."""
        if not candidates:
            return None
        
        def spherical_distance(a: UnifiedExperiment, b: UnifiedExperiment) -> float:
            # Great circle distance on unit sphere
            cos_dist = (
                math.sin(a.theta) * math.sin(b.theta) * 
                math.cos(a.phi - b.phi) +
                math.cos(a.theta) * math.cos(b.theta)
            )
            return math.acos(max(-1, min(1, cos_dist)))
        
        return min(candidates, key=lambda c: spherical_distance(exp, c))
    
    def add_experiment(
        self,
        data: Dict[str, Any],
        exp_class: Optional[ExperimentClass] = None,
        origin: ExperimentOrigin = ExperimentOrigin.LOCAL,
    ) -> UnifiedExperiment:
        """Add a new experiment to the registry."""
        if exp_class is None:
            exp_class = classify_experiment(data)
        
        exp_id = data.get("id", f"exp_{len(self.experiments)}")
        
        # Create minimal metadata
        metadata = ExperimentMetadata(
            experiment_class=exp_class,
            origin=origin,
            experiment_id=exp_id,
            timestamp=datetime.now().isoformat(),
            coherence=data.get("coherence", 0.0),
            entropy=data.get("entropy", 0.0),
        )
        
        theta, phi, depth = self._assign_coordinates(exp_class, metadata)
        color = self._assign_color(
            exp_class,
            metadata.coherence,
            metadata.entropy,
        )
        
        experiment = UnifiedExperiment(
            experiment_id=exp_id,
            metadata=metadata,
            raw_data=data,
            counts=data.get("counts", {}),
            theta=theta,
            phi=phi,
            depth=depth,
            color=color,
        )
        
        self.experiments[exp_id] = experiment
        return experiment
    
    def get_by_class(
        self,
        exp_class: ExperimentClass,
    ) -> List[UnifiedExperiment]:
        """Get all experiments of a specific class."""
        return [
            exp for exp in self.experiments.values()
            if exp.metadata.experiment_class == exp_class
        ]
    
    def get_by_origin(
        self,
        origin: ExperimentOrigin,
    ) -> List[UnifiedExperiment]:
        """Get all experiments from a specific origin."""
        return [
            exp for exp in self.experiments.values()
            if exp.metadata.origin == origin
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        by_class = {}
        by_origin = {}
        
        for exp in self.experiments.values():
            class_name = exp.metadata.experiment_class.value
            origin_name = exp.metadata.origin.value
            
            by_class[class_name] = by_class.get(class_name, 0) + 1
            by_origin[origin_name] = by_origin.get(origin_name, 0) + 1
        
        return {
            "total": len(self.experiments),
            "by_class": by_class,
            "by_origin": by_origin,
        }
    
    def export_surface(self) -> Dict[str, Any]:
        """Export all experiments as unified surface data."""
        vertices = []
        edges = []
        seen_edges = set()
        
        for exp in self.experiments.values():
            vertices.append(exp.to_surface_dict())
            
            # Add edges for connections
            for connected_id in exp.connected_experiments:
                edge_key = tuple(sorted([exp.experiment_id, connected_id]))
                if edge_key not in seen_edges and connected_id in self.experiments:
                    seen_edges.add(edge_key)
                    edges.append({
                        "from": exp.experiment_id,
                        "to": connected_id,
                        "type": "relation",
                    })
        
        # Statistics
        stats = self.get_statistics()
        
        return {
            "vertices": vertices,
            "edges": edges,
            "statistics": stats,
            "generated_at": datetime.now().isoformat(),
            "version": "2.0",
        }
    
    def export_to_file(self, filepath: str) -> None:
        """Export surface to JSON file."""
        surface = self.export_surface()
        with open(filepath, 'w') as f:
            json.dump(surface, f, indent=2)
        print(f"Exported {len(self.experiments)} experiments to {filepath}")


# ═══════════════════════════════════════════════════════════════════
# Convenience functions
# ═══════════════════════════════════════════════════════════════════

def build_unified_surface(base_path: str = ".") -> Dict[str, Any]:
    """Build unified surface from all available experiments."""
    registry = ExperimentRegistry(base_path)
    count = registry.load_all()
    print(f"Loaded {count} experiments from all sources")
    
    stats = registry.get_statistics()
    print(f"  By class: {stats['by_class']}")
    print(f"  By origin: {stats['by_origin']}")
    
    return registry.export_surface()


def load_registry(base_path: str = ".") -> ExperimentRegistry:
    """Load and return a populated registry."""
    registry = ExperimentRegistry(base_path)
    registry.load_all()
    return registry
