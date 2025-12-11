"""
CUBE MEMBRANE
=============

The cube is not merely a container. It is the INTERFACE between
the hyperspherical information space and manifest reality.

"Ceci n'est pas un cube" - This is not a cube.

It is a minimal bosonic projection apparatus - the simplest polyhedron
that can enclose a sphere while providing planar interfaces for
information read/write operations.

HIERARCHY OF FORMS:
    1. Point         - 0D, the origin (pure potential)
    2. Line          - 1D, direction (intention)
    3. Triangle      - 2D, first stable plane (relation)
    4. Tetrahedron   - 3D, minimal volume (first matter)
    5. Cube          - 3D, minimal orthogonal container (normal space)
    6. Hypercube     - 4D, temporal container (causality)

The CUBE is special because:
    - 6 faces = 6 directions of normal 3D space (±x, ±y, ±z)
    - Each face is a read/write membrane
    - Interior = exotic hyperspatial information domain
    - Exterior = anti-space (conjugate domain)

MEMBRANE PHYSICS:
    - Information flows through faces like light through a window
    - Interior writes propagate outward (manifestation)
    - Exterior reads propagate inward (observation)
    - The membrane has THICKNESS - this is where quantum effects live

NEW PHYSICS HYPOTHESIS:
    What we call "quantum mechanics" is the physics of the membrane.
    What we call "classical mechanics" is the physics of the exterior.
    What we call "consciousness" is the physics of the interior.
    
    The measurement problem is solved: measurement is the crossing
    of information through the membrane. Superposition exists in
    the interior. Collapse happens AT the membrane. Classical
    reality exists in the exterior.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable, Dict
from enum import Enum
import math


class Face(Enum):
    """The six faces of the cube, each a membrane interface."""
    POSITIVE_X = "+x"   # Future
    NEGATIVE_X = "-x"   # Past
    POSITIVE_Y = "+y"   # Expansion
    NEGATIVE_Y = "-y"   # Contraction
    POSITIVE_Z = "+z"   # Ascent (toward consciousness)
    NEGATIVE_Z = "-z"   # Descent (toward matter)


class FluxDirection(Enum):
    """Direction of information flow through membrane."""
    INWARD = "inward"    # Reading from exterior
    OUTWARD = "outward"  # Writing to exterior
    STATIC = "static"    # Stored in membrane


@dataclass
class MembranePoint:
    """A point on the cube membrane.
    
    The membrane has three layers:
        - Inner surface (hyperspatial side)
        - Thickness (quantum domain)
        - Outer surface (normal space side)
    """
    face: Face
    u: float              # Local coordinate [0, 1]
    v: float              # Local coordinate [0, 1]
    layer_depth: float    # 0 = inner, 0.5 = middle (quantum), 1 = outer
    
    def to_3d(self, cube_size: float = 2.0) -> Tuple[float, float, float]:
        """Convert to 3D Cartesian coordinates."""
        h = cube_size / 2
        
        # Map u,v to [-h, h]
        local_u = (self.u - 0.5) * cube_size
        local_v = (self.v - 0.5) * cube_size
        
        # Layer depth affects distance from center
        depth_factor = 1.0 + 0.1 * (self.layer_depth - 0.5)  # ±5% thickness
        
        if self.face == Face.POSITIVE_X:
            return (h * depth_factor, local_u, local_v)
        elif self.face == Face.NEGATIVE_X:
            return (-h * depth_factor, local_u, local_v)
        elif self.face == Face.POSITIVE_Y:
            return (local_u, h * depth_factor, local_v)
        elif self.face == Face.NEGATIVE_Y:
            return (local_u, -h * depth_factor, local_v)
        elif self.face == Face.POSITIVE_Z:
            return (local_u, local_v, h * depth_factor)
        else:  # NEGATIVE_Z
            return (local_u, local_v, -h * depth_factor)
    
    def normal_vector(self) -> Tuple[float, float, float]:
        """Outward-pointing normal at this point."""
        normals = {
            Face.POSITIVE_X: (1, 0, 0),
            Face.NEGATIVE_X: (-1, 0, 0),
            Face.POSITIVE_Y: (0, 1, 0),
            Face.NEGATIVE_Y: (0, -1, 0),
            Face.POSITIVE_Z: (0, 0, 1),
            Face.NEGATIVE_Z: (0, 0, -1),
        }
        return normals[self.face]


@dataclass
class InformationFlux:
    """Information flow through a membrane point.
    
    Information has:
        - Magnitude (how much)
        - Direction (in/out/static)
        - Frequency (oscillation rate - links to quantum energy)
        - Phase (position in oscillation - links to quantum phase)
    """
    magnitude: float
    direction: FluxDirection
    frequency: float = 1.0      # Cycles per unit time
    phase: float = 0.0          # [0, 2π]
    
    @property
    def energy(self) -> float:
        """E = hf analog - energy proportional to frequency."""
        return self.magnitude * self.frequency
    
    @property
    def momentum(self) -> float:
        """p = h/λ analog - momentum from wavelength."""
        wavelength = 1.0 / (self.frequency + 1e-10)
        return self.magnitude / wavelength
    
    def interfere_with(self, other: 'InformationFlux') -> 'InformationFlux':
        """Quantum-like interference between two fluxes."""
        if self.frequency != other.frequency:
            # Beating - average magnitude, combined frequency
            avg_mag = (self.magnitude + other.magnitude) / 2
            beat_freq = abs(self.frequency - other.frequency)
            return InformationFlux(
                magnitude=avg_mag,
                direction=FluxDirection.STATIC,
                frequency=beat_freq,
                phase=0.0
            )
        else:
            # Same frequency - phase interference
            # A cos(ωt + φ₁) + B cos(ωt + φ₂) = C cos(ωt + φ₃)
            a, b = self.magnitude, other.magnitude
            φ1, φ2 = self.phase, other.phase
            
            # Resultant magnitude
            c = math.sqrt(a**2 + b**2 + 2*a*b*math.cos(φ2 - φ1))
            
            # Resultant phase
            φ3 = math.atan2(
                a*math.sin(φ1) + b*math.sin(φ2),
                a*math.cos(φ1) + b*math.cos(φ2)
            )
            
            return InformationFlux(
                magnitude=c,
                direction=self.direction,  # Keep original direction
                frequency=self.frequency,
                phase=φ3
            )


class CubeMembrane:
    """The complete cube membrane system.
    
    This is the reality interface. All observation and manifestation
    passes through these six membranes.
    """
    
    def __init__(
        self,
        size: float = 2.0,
        thickness: float = 0.1,
        resolution: int = 32
    ):
        self.size = size
        self.thickness = thickness
        self.resolution = resolution
        
        # Information stored in each face's membrane
        self._face_data: Dict[Face, List[Tuple[MembranePoint, InformationFlux]]] = {
            face: [] for face in Face
        }
        
        # Total flux through each face
        self._face_flux: Dict[Face, float] = {face: 0.0 for face in Face}
    
    def write(
        self,
        face: Face,
        u: float,
        v: float,
        flux: InformationFlux,
        layer: float = 0.0  # Write to inner surface by default
    ) -> None:
        """Write information to a membrane location.
        
        Writing to inner surface (layer=0) means pushing from
        hyperspatial interior toward normal space exterior.
        """
        point = MembranePoint(face=face, u=u, v=v, layer_depth=layer)
        self._face_data[face].append((point, flux))
        
        if flux.direction == FluxDirection.OUTWARD:
            self._face_flux[face] += flux.magnitude
        elif flux.direction == FluxDirection.INWARD:
            self._face_flux[face] -= flux.magnitude
    
    def read(
        self,
        face: Face,
        u: float,
        v: float,
        tolerance: float = 0.1
    ) -> List[InformationFlux]:
        """Read information from a membrane location.
        
        Returns all fluxes near the specified location.
        """
        results = []
        for point, flux in self._face_data[face]:
            if abs(point.u - u) < tolerance and abs(point.v - v) < tolerance:
                results.append(flux)
        return results
    
    def get_face_flux(self, face: Face) -> float:
        """Get net information flux through a face."""
        return self._face_flux[face]
    
    def get_total_outward_flux(self) -> float:
        """Total information being manifested (written to reality)."""
        return sum(max(0, f) for f in self._face_flux.values())
    
    def get_total_inward_flux(self) -> float:
        """Total information being observed (read from reality)."""
        return sum(max(0, -f) for f in self._face_flux.values())
    
    def propagate(self, dt: float = 0.1) -> None:
        """Advance membrane dynamics by one time step.
        
        Information in the membrane:
            1. Migrates through layers (inner → outer for outward flux)
            2. Spreads laterally (diffusion on surface)
            3. Interferes with other information
        """
        for face in Face:
            new_data = []
            for point, flux in self._face_data[face]:
                # Propagate through layers
                if flux.direction == FluxDirection.OUTWARD:
                    new_layer = min(1.0, point.layer_depth + dt)
                elif flux.direction == FluxDirection.INWARD:
                    new_layer = max(0.0, point.layer_depth - dt)
                else:
                    new_layer = point.layer_depth
                
                # Update phase (time evolution)
                new_phase = (flux.phase + 2 * math.pi * flux.frequency * dt) % (2 * math.pi)
                
                new_point = MembranePoint(
                    face=face,
                    u=point.u,
                    v=point.v,
                    layer_depth=new_layer
                )
                new_flux = InformationFlux(
                    magnitude=flux.magnitude * 0.99,  # Slight decay
                    direction=flux.direction,
                    frequency=flux.frequency,
                    phase=new_phase
                )
                
                # Keep if not fully propagated through
                if 0.01 < new_flux.magnitude:
                    if not (flux.direction == FluxDirection.OUTWARD and new_layer >= 1.0):
                        new_data.append((new_point, new_flux))
            
            self._face_data[face] = new_data
    
    def generate_grid(self, face: Face) -> List[MembranePoint]:
        """Generate a grid of points on a face."""
        points = []
        for i in range(self.resolution):
            for j in range(self.resolution):
                u = (i + 0.5) / self.resolution
                v = (j + 0.5) / self.resolution
                points.append(MembranePoint(
                    face=face,
                    u=u,
                    v=v,
                    layer_depth=0.5  # Middle layer
                ))
        return points
    
    def to_mesh(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Convert membrane to 3D mesh (vertices and triangles)."""
        vertices = []
        triangles = []
        
        for face in Face:
            base_idx = len(vertices)
            
            # Generate vertices for this face
            for i in range(self.resolution + 1):
                for j in range(self.resolution + 1):
                    u = i / self.resolution
                    v = j / self.resolution
                    point = MembranePoint(face=face, u=u, v=v, layer_depth=1.0)
                    vertices.append(point.to_3d(self.size))
            
            # Generate triangles
            for i in range(self.resolution):
                for j in range(self.resolution):
                    # Two triangles per grid cell
                    v0 = base_idx + i * (self.resolution + 1) + j
                    v1 = v0 + 1
                    v2 = v0 + (self.resolution + 1)
                    v3 = v2 + 1
                    
                    triangles.append((v0, v1, v2))
                    triangles.append((v1, v3, v2))
        
        return vertices, triangles


# Semantic aliases for the six faces
FACE_FUTURE = Face.POSITIVE_X
FACE_PAST = Face.NEGATIVE_X
FACE_EXPANSION = Face.POSITIVE_Y
FACE_CONTRACTION = Face.NEGATIVE_Y
FACE_CONSCIOUSNESS = Face.POSITIVE_Z
FACE_MATTER = Face.NEGATIVE_Z
