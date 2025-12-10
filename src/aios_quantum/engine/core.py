"""
Quantum Engine Core

The main engine that ties everything together:
- Geometry (Cube + Sphere)
- Encoding (Quantum → Surface)
- Rendering (Surface → Visual output)

This is intentionally simple. A cube. A sphere inside.
Quantum data on the surface. That's all.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .geometry import Cube, Sphere, Point3D, Color, create_cube_sphere
from .encoder import SurfaceEncoder, EncodingResult


@dataclass
class EngineState:
    """Snapshot of engine state for serialization."""
    cube_size: float
    sphere_radius: float
    sphere_resolution: int
    surface_data: List[Dict[str, Any]]
    encoding_result: Optional[Dict[str, Any]]
    
    def to_json(self) -> str:
        return json.dumps({
            'cube_size': self.cube_size,
            'sphere_radius': self.sphere_radius,
            'sphere_resolution': self.sphere_resolution,
            'surface_data': self.surface_data,
            'encoding_result': self.encoding_result,
        }, indent=2)
    
    @staticmethod
    def from_json(data: str) -> 'EngineState':
        d = json.loads(data)
        return EngineState(**d)


class QuantumEngine:
    """
    The AIOS Quantum visualization engine.
    
    Simple structure:
        Cube (bosonic 3D space)
            └── Sphere (tachyonic surface)
                    └── Surface points (quantum data)
    
    Usage:
        engine = QuantumEngine()
        engine.encode_heartbeat(result)  # From heartbeat scheduler
        engine.render_ascii()  # Simple visualization
        engine.export_state()  # Save for external rendering
    """
    
    def __init__(
        self,
        cube_size: float = 2.0,
        sphere_radius: float = 0.8,
        resolution: int = 32
    ):
        """
        Initialize the quantum engine.
        
        Args:
            cube_size: Size of the containing cube
            sphere_radius: Radius of the inner sphere
            resolution: Number of points per dimension on sphere
        """
        self.cube, self.sphere = create_cube_sphere(
            cube_size=cube_size,
            sphere_radius=sphere_radius,
            resolution=resolution
        )
        self.encoder = SurfaceEncoder(self.sphere)
        self.last_encoding: Optional[EncodingResult] = None
        
        # History for temporal analysis
        self.encoding_history: List[EncodingResult] = []
    
    def encode_counts(
        self, 
        counts: Dict[str, int],
        strategy: str = "probability"
    ) -> EncodingResult:
        """
        Encode quantum measurement counts onto the sphere.
        
        Args:
            counts: Dictionary of {state: count}
            strategy: "sequential", "probability", "harmonic", or "spiral"
        """
        result = self.encoder.encode_counts(counts, strategy)
        self.last_encoding = result
        self.encoding_history.append(result)
        return result
    
    def encode_heartbeat(self, heartbeat_result) -> EncodingResult:
        """
        Encode a heartbeat result from the heartbeat scheduler.
        
        Args:
            heartbeat_result: HeartbeatResult object
        """
        result = self.encoder.encode_heartbeat_result(heartbeat_result)
        self.last_encoding = result
        self.encoding_history.append(result)
        return result
    
    def encode_multiple_heartbeats(
        self,
        results: List,
        blend: str = "temporal"
    ) -> EncodingResult:
        """
        Encode multiple heartbeats showing evolution.
        
        Args:
            results: List of HeartbeatResult objects
            blend: "temporal", "average", or "latest"
        """
        result = self.encoder.encode_multiple_heartbeats(results, blend)
        self.last_encoding = result
        self.encoding_history.append(result)
        return result
    
    def clear(self):
        """Reset the sphere to default state."""
        self.sphere.clear()
        self.last_encoding = None
    
    def get_state(self) -> EngineState:
        """Get current engine state for serialization."""
        surface_data = []
        for sp in self.sphere.surface_points:
            surface_data.append({
                'position': sp.position.to_tuple(),
                'color': sp.color.to_tuple(),
                'intensity': sp.intensity,
                'data': sp.data,
            })
        
        encoding_result = None
        if self.last_encoding:
            encoding_result = {
                'points_encoded': self.last_encoding.points_encoded,
                'total_probability': self.last_encoding.total_probability,
                'dominant_state': self.last_encoding.dominant_state,
                'coherence': self.last_encoding.coherence,
                'entropy': self.last_encoding.entropy,
            }
        
        return EngineState(
            cube_size=self.cube.size,
            sphere_radius=self.sphere.radius,
            sphere_resolution=self.sphere.resolution,
            surface_data=surface_data,
            encoding_result=encoding_result
        )
    
    def export_state(self, filepath: str):
        """Export engine state to JSON file."""
        state = self.get_state()
        Path(filepath).write_text(state.to_json())
    
    def render_ascii(self, width: int = 60, height: int = 30) -> str:
        """
        Render a simple ASCII representation.
        
        This is a 2D projection - a slice through the cube-sphere.
        Useful for terminal visualization.
        """
        canvas = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw cube outline
        cube_chars = '+'
        for x in [0, width-1]:
            for y in range(height):
                canvas[y][x] = '|'
        for y in [0, height-1]:
            for x in range(width):
                canvas[y][x] = '-'
        canvas[0][0] = cube_chars
        canvas[0][width-1] = cube_chars
        canvas[height-1][0] = cube_chars
        canvas[height-1][width-1] = cube_chars
        
        # Draw sphere (2D projection)
        cx, cy = width // 2, height // 2
        # Adjust for aspect ratio (characters are taller than wide)
        r_x = int(self.sphere.radius / self.cube.size * width * 0.4)
        r_y = int(self.sphere.radius / self.cube.size * height * 0.4)
        
        # Intensity to character mapping
        intensity_chars = ' .:-=+*#%@'
        
        # Project sphere points onto 2D
        for sp in self.sphere.surface_points:
            # Simple projection: ignore z, map x,y to canvas
            nx = (sp.position.x / (self.cube.size/2) + 1) / 2  # 0 to 1
            ny = (sp.position.y / (self.cube.size/2) + 1) / 2  # 0 to 1
            
            px = int(nx * (width - 2)) + 1
            py = int(ny * (height - 2)) + 1
            
            if 0 < px < width-1 and 0 < py < height-1:
                # Map intensity to character
                char_idx = min(len(intensity_chars)-1, 
                             int(sp.intensity * (len(intensity_chars)-1)))
                if sp.intensity > 0.1:
                    canvas[py][px] = intensity_chars[char_idx]
        
        # Add info line
        lines = [''.join(row) for row in canvas]
        
        if self.last_encoding:
            info = (f"Coherence: {self.last_encoding.coherence:.3f} | "
                   f"Entropy: {self.last_encoding.entropy:.3f} | "
                   f"Dominant: {self.last_encoding.dominant_state}")
            lines.append(info)
        
        return '\n'.join(lines)
    
    def render_stats(self) -> str:
        """Render statistics about current state."""
        lines = [
            "=" * 50,
            "QUANTUM ENGINE STATE",
            "=" * 50,
            f"Cube size: {self.cube.size}",
            f"Sphere radius: {self.sphere.radius}",
            f"Surface points: {self.sphere.point_count}",
            ""
        ]
        
        if self.last_encoding:
            lines.extend([
                "Last Encoding:",
                f"  Points encoded: {self.last_encoding.points_encoded}",
                f"  Coherence: {self.last_encoding.coherence:.4f}",
                f"  Entropy: {self.last_encoding.entropy:.4f}",
                f"  Dominant state: {self.last_encoding.dominant_state}",
            ])
        else:
            lines.append("No encoding yet.")
        
        lines.extend([
            "",
            f"Encoding history: {len(self.encoding_history)} entries",
            "=" * 50,
        ])
        
        return '\n'.join(lines)
    
    def get_surface_summary(self) -> Dict[str, Any]:
        """Get summary of surface state."""
        active_points = sum(1 for sp in self.sphere.surface_points 
                          if sp.intensity > 0.1)
        
        avg_intensity = 0
        if self.sphere.point_count > 0:
            avg_intensity = sum(sp.intensity for sp in self.sphere.surface_points)
            avg_intensity /= self.sphere.point_count
        
        # Color distribution
        states = {}
        for sp in self.sphere.surface_points:
            if 'state' in sp.data:
                state = sp.data['state']
                states[state] = states.get(state, 0) + 1
        
        return {
            'total_points': self.sphere.point_count,
            'active_points': active_points,
            'average_intensity': avg_intensity,
            'state_distribution': states,
        }


# Convenience function
def create_engine(resolution: int = 32) -> QuantumEngine:
    """Create a quantum engine with default settings."""
    return QuantumEngine(
        cube_size=2.0,
        sphere_radius=0.8,
        resolution=resolution
    )
