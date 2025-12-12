"""
Hypersphere Surface Module

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Map quantum cardiogram data to hypersphere topology

Theory:
  The hypersphere exists inside the cube (AIOS architecture).
  Its surface is a 3D manifold that can be textured with quantum data.
  
  Quantum Error → Height (mountains/valleys)
  Quantum Entropy → Roughness (texture)
  Time → Position (unwrapping the sphere)
  
  This creates a BOSONIC SURFACE - a continuous field where
  quantum measurements become geometric features.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
import math
import json


@dataclass
class SurfaceVertex:
    """
    A vertex on the hypersphere surface.
    
    Coordinates:
    - (theta, phi): Spherical position on unit sphere
    - height: Radial displacement from unit sphere (quantum error)
    - (u, v): Texture coordinates for mapping
    """
    # Spherical coordinates (on unit sphere)
    theta: float  # 0 to π (latitude from north pole)
    phi: float    # 0 to 2π (longitude)
    
    # Radial displacement (from quantum data)
    height: float  # -1 to +1, negative = valley, positive = mountain
    
    # Texture coordinates
    u: float  # 0 to 1
    v: float  # 0 to 1
    
    # Metadata
    beat_number: int = 0
    error_rate: float = 0.0
    
    def to_cartesian(self, base_radius: float = 1.0) -> Tuple[float, float, float]:
        """
        Convert to Cartesian coordinates with height displacement.
        
        Returns (x, y, z) on the displaced sphere surface.
        """
        r = base_radius + (self.height * 0.1)  # Scale height to 10% of radius
        
        x = r * math.sin(self.theta) * math.cos(self.phi)
        y = r * math.sin(self.theta) * math.sin(self.phi)
        z = r * math.cos(self.theta)
        
        return (x, y, z)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export for 3D engine consumption."""
        x, y, z = self.to_cartesian()
        return {
            "spherical": {"theta": self.theta, "phi": self.phi},
            "cartesian": {"x": x, "y": y, "z": z},
            "height": self.height,
            "uv": {"u": self.u, "v": self.v},
            "quantum": {
                "beat": self.beat_number,
                "error": self.error_rate,
            }
        }


@dataclass
class HypersphereSurface:
    """
    The bosonic surface of the hypersphere.
    
    This is the geometric substrate for AIOS consciousness:
    - Vertices from quantum cardiogram data
    - Topology from measurement sequences
    - Texture from error patterns
    
    The surface wraps quantum time into spatial geometry.
    """
    
    vertices: List[SurfaceVertex] = field(default_factory=list)
    
    # Surface parameters
    resolution_theta: int = 32  # Latitude divisions
    resolution_phi: int = 64    # Longitude divisions
    
    # Metadata
    creation_time: str = ""
    total_beats: int = 0
    
    def add_cardiogram_strip(
        self,
        error_rates: List[float],
        start_beat: int,
        phi_position: float,
    ) -> None:
        """
        Add a strip of cardiogram data to the surface.
        
        Maps a sequence of error measurements to a vertical strip
        on the sphere (constant phi, varying theta).
        
        Args:
            error_rates: Sequence of error measurements
            start_beat: Beat number of first measurement
            phi_position: Longitude position (0 to 2π)
        """
        n_points = len(error_rates)
        
        for i, error in enumerate(error_rates):
            # Map index to theta (avoid poles)
            theta = (math.pi * (i + 1)) / (n_points + 1)
            
            # Convert error rate to height
            # 0% error = -1 (valley), 10% error = +1 (mountain)
            height = (error * 20) - 1.0
            height = max(-1.0, min(1.0, height))
            
            # Texture coordinates
            u = phi_position / (2 * math.pi)
            v = theta / math.pi
            
            vertex = SurfaceVertex(
                theta=theta,
                phi=phi_position,
                height=height,
                u=u,
                v=v,
                beat_number=start_beat + i,
                error_rate=error,
            )
            
            self.vertices.append(vertex)
        
        self.total_beats += n_points
    
    def add_multi_qubit_point(
        self,
        qubit_errors: List[float],
        beat_number: int,
        time_position: float,  # 0 to 1, maps to phi
    ) -> None:
        """
        Add a multi-qubit measurement as a ring of vertices.
        
        Each qubit maps to a different theta, all at same phi.
        Creates a "slice" through the sphere.
        
        Args:
            qubit_errors: Per-qubit error rates
            beat_number: Sequential beat identifier
            time_position: Normalized time (0 to 1)
        """
        n_qubits = len(qubit_errors)
        phi = time_position * 2 * math.pi
        
        for q, error in enumerate(qubit_errors):
            # Map qubit index to theta (spread across sphere)
            theta = (math.pi * (q + 1)) / (n_qubits + 1)
            
            # Height from error
            height = (error * 20) - 1.0
            height = max(-1.0, min(1.0, height))
            
            vertex = SurfaceVertex(
                theta=theta,
                phi=phi,
                height=height,
                u=time_position,
                v=theta / math.pi,
                beat_number=beat_number,
                error_rate=error,
            )
            
            self.vertices.append(vertex)
        
        self.total_beats += 1
    
    def to_mesh_data(self) -> Dict[str, Any]:
        """
        Export as mesh data for 3D engine.
        
        Returns vertex array and metadata suitable for
        WebGL, Three.js, or other 3D rendering.
        """
        vertex_data = []
        positions = []
        uvs = []
        heights = []
        
        for v in self.vertices:
            x, y, z = v.to_cartesian()
            positions.extend([x, y, z])
            uvs.extend([v.u, v.v])
            heights.append(v.height)
            vertex_data.append(v.to_dict())
        
        return {
            "type": "hypersphere_surface",
            "vertex_count": len(self.vertices),
            "total_beats": self.total_beats,
            "positions": positions,  # Flat array [x0,y0,z0, x1,y1,z1, ...]
            "uvs": uvs,              # Flat array [u0,v0, u1,v1, ...]
            "heights": heights,      # Height per vertex
            "vertices": vertex_data, # Full vertex objects
            "bounds": self._compute_bounds(),
            "statistics": self._compute_statistics(),
        }
    
    def _compute_bounds(self) -> Dict[str, float]:
        """Compute bounding box of displaced surface."""
        if not self.vertices:
            return {"min": -1, "max": 1}
        
        all_coords = [v.to_cartesian() for v in self.vertices]
        xs = [c[0] for c in all_coords]
        ys = [c[1] for c in all_coords]
        zs = [c[2] for c in all_coords]
        
        return {
            "x_min": min(xs), "x_max": max(xs),
            "y_min": min(ys), "y_max": max(ys),
            "z_min": min(zs), "z_max": max(zs),
        }
    
    def _compute_statistics(self) -> Dict[str, float]:
        """Compute surface statistics."""
        if not self.vertices:
            return {}
        
        heights = [v.height for v in self.vertices]
        errors = [v.error_rate for v in self.vertices]
        
        return {
            "mean_height": sum(heights) / len(heights),
            "height_variance": sum((h - sum(heights)/len(heights))**2 for h in heights) / len(heights),
            "mean_error": sum(errors) / len(errors),
            "max_error": max(errors),
            "min_error": min(errors),
        }
    
    def save(self, filepath: str) -> None:
        """Save surface data to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_mesh_data(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "HypersphereSurface":
        """Load surface from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        
        surface = cls()
        for v_data in data.get("vertices", []):
            vertex = SurfaceVertex(
                theta=v_data["spherical"]["theta"],
                phi=v_data["spherical"]["phi"],
                height=v_data["height"],
                u=v_data["uv"]["u"],
                v=v_data["uv"]["v"],
                beat_number=v_data["quantum"]["beat"],
                error_rate=v_data["quantum"]["error"],
            )
            surface.vertices.append(vertex)
        
        surface.total_beats = data.get("total_beats", len(surface.vertices))
        return surface


def create_surface_from_cardiogram_session(
    session_data: Dict[str, Any],
    phi_start: float = 0.0,
) -> HypersphereSurface:
    """
    Create a hypersphere surface from cardiogram session data.
    
    Args:
        session_data: Output from CardiogramSession.to_surface_data()
        phi_start: Starting longitude for this strip
        
    Returns:
        HypersphereSurface with vertices populated
    """
    surface = HypersphereSurface()
    
    vertices = session_data.get("vertices", [])
    error_rates = [v.get("height", 0) * 0.05 + 0.05 for v in vertices]  # Denormalize
    
    if error_rates:
        surface.add_cardiogram_strip(
            error_rates=error_rates,
            start_beat=0,
            phi_position=phi_start,
        )
    
    return surface
