"""
Geometry Primitives

The fundamental shapes of our visualization:
- Cube: The bosonic container (3D space)
- Sphere: The tachyonic surface (consciousness boundary)
- Point3D: A location in space
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Iterator
import colorsys


@dataclass
class Point3D:
    """A point in 3D space."""
    x: float
    y: float
    z: float
    
    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Point3D':
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Point3D':
        m = self.magnitude()
        if m == 0:
            return Point3D(0, 0, 0)
        return Point3D(self.x/m, self.y/m, self.z/m)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def to_spherical(self) -> Tuple[float, float, float]:
        """Convert to spherical coordinates (r, theta, phi)."""
        r = self.magnitude()
        if r == 0:
            return (0, 0, 0)
        theta = math.acos(self.z / r)  # polar angle [0, π]
        phi = math.atan2(self.y, self.x)  # azimuthal angle [-π, π]
        return (r, theta, phi)
    
    @staticmethod
    def from_spherical(r: float, theta: float, phi: float) -> 'Point3D':
        """Create from spherical coordinates."""
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        return Point3D(x, y, z)


@dataclass
class Color:
    """RGB color with alpha."""
    r: float  # 0-1
    g: float  # 0-1
    b: float  # 0-1
    a: float = 1.0  # 0-1
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)
    
    def to_hex(self) -> str:
        return f"#{int(self.r*255):02x}{int(self.g*255):02x}{int(self.b*255):02x}"
    
    @staticmethod
    def from_hsv(h: float, s: float, v: float, a: float = 1.0) -> 'Color':
        """Create from HSV (hue 0-1, saturation 0-1, value 0-1)."""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return Color(r, g, b, a)
    
    @staticmethod
    def from_quantum_state(state: str, probability: float) -> 'Color':
        """
        Create color from quantum measurement.
        
        State determines hue (based on bit pattern).
        Probability determines brightness.
        """
        # Convert state to hue (0-1)
        if state:
            # Use state as binary number, normalize to [0, 1]
            try:
                state_int = int(state, 2)
                max_val = 2 ** len(state) - 1
                hue = state_int / max_val if max_val > 0 else 0
            except ValueError:
                hue = 0
        else:
            hue = 0
        
        # Probability affects saturation and value
        saturation = 0.7 + 0.3 * probability  # 0.7-1.0
        value = 0.3 + 0.7 * probability  # 0.3-1.0
        
        return Color.from_hsv(hue, saturation, value)


@dataclass
class SurfacePoint:
    """A point on a surface with color and intensity."""
    position: Point3D
    color: Color
    intensity: float = 1.0
    data: dict = field(default_factory=dict)  # Extra quantum data


class Cube:
    """
    The bosonic cube - our 3D container.
    
    Represents observable 3D space, the framework within which
    the tachyonic sphere exists.
    """
    
    def __init__(self, size: float = 2.0, center: Optional[Point3D] = None):
        self.size = size
        self.center = center or Point3D(0, 0, 0)
        self.half = size / 2
    
    @property
    def vertices(self) -> List[Point3D]:
        """The 8 vertices of the cube."""
        h = self.half
        c = self.center
        return [
            Point3D(c.x - h, c.y - h, c.z - h),
            Point3D(c.x + h, c.y - h, c.z - h),
            Point3D(c.x + h, c.y + h, c.z - h),
            Point3D(c.x - h, c.y + h, c.z - h),
            Point3D(c.x - h, c.y - h, c.z + h),
            Point3D(c.x + h, c.y - h, c.z + h),
            Point3D(c.x + h, c.y + h, c.z + h),
            Point3D(c.x - h, c.y + h, c.z + h),
        ]
    
    @property
    def edges(self) -> List[Tuple[int, int]]:
        """Vertex indices for the 12 edges."""
        return [
            (0, 1), (1, 2), (2, 3), (3, 0),  # bottom
            (4, 5), (5, 6), (6, 7), (7, 4),  # top
            (0, 4), (1, 5), (2, 6), (3, 7),  # verticals
        ]
    
    def contains(self, point: Point3D) -> bool:
        """Check if point is inside the cube."""
        return (
            abs(point.x - self.center.x) <= self.half and
            abs(point.y - self.center.y) <= self.half and
            abs(point.z - self.center.z) <= self.half
        )


class Sphere:
    """
    The tachyonic sphere - consciousness boundary.
    
    The surface of this sphere is where we encode quantum
    measurement results. Each point on the surface can hold
    color, intensity, and data from heartbeat results.
    """
    
    def __init__(
        self, 
        radius: float = 0.8, 
        center: Optional[Point3D] = None,
        resolution: int = 32
    ):
        self.radius = radius
        self.center = center or Point3D(0, 0, 0)
        self.resolution = resolution  # Points per dimension
        
        # Surface data - encoded quantum results
        self.surface_points: List[SurfacePoint] = []
        self._generate_surface_grid()
    
    def _generate_surface_grid(self):
        """Generate a grid of points on the sphere surface."""
        self.surface_points = []
        
        for i in range(self.resolution):
            theta = math.pi * i / (self.resolution - 1)  # 0 to π
            
            # Fewer points near poles
            phi_count = max(1, int(self.resolution * math.sin(theta)))
            
            for j in range(phi_count):
                phi = 2 * math.pi * j / phi_count  # 0 to 2π
                
                pos = Point3D.from_spherical(self.radius, theta, phi)
                pos = pos + self.center
                
                self.surface_points.append(SurfacePoint(
                    position=pos,
                    color=Color(0.1, 0.1, 0.2, 0.5),  # Default dark blue
                    intensity=0.0
                ))
    
    def get_point_at(self, theta: float, phi: float) -> Optional[SurfacePoint]:
        """Get the surface point closest to given spherical coordinates."""
        target = Point3D.from_spherical(self.radius, theta, phi)
        target = target + self.center
        
        closest = None
        min_dist = float('inf')
        
        for sp in self.surface_points:
            dist = (sp.position - target).magnitude()
            if dist < min_dist:
                min_dist = dist
                closest = sp
        
        return closest
    
    def set_point_color(self, index: int, color: Color, intensity: float = 1.0):
        """Set color and intensity of a surface point by index."""
        if 0 <= index < len(self.surface_points):
            self.surface_points[index].color = color
            self.surface_points[index].intensity = intensity
    
    def encode_quantum_state(
        self, 
        state: str, 
        probability: float, 
        index: int
    ):
        """
        Encode a quantum measurement state onto a surface point.
        
        This is the key operation - mapping quantum results to visual space.
        """
        if 0 <= index < len(self.surface_points):
            color = Color.from_quantum_state(state, probability)
            self.surface_points[index].color = color
            self.surface_points[index].intensity = probability
            self.surface_points[index].data = {
                'state': state,
                'probability': probability,
            }
    
    def clear(self):
        """Reset all surface points to default."""
        for sp in self.surface_points:
            sp.color = Color(0.1, 0.1, 0.2, 0.5)
            sp.intensity = 0.0
            sp.data = {}
    
    def iter_surface(self) -> Iterator[SurfacePoint]:
        """Iterate over all surface points."""
        return iter(self.surface_points)
    
    @property
    def point_count(self) -> int:
        return len(self.surface_points)


# Convenience functions
def create_cube_sphere(
    cube_size: float = 2.0,
    sphere_radius: float = 0.8,
    resolution: int = 32
) -> Tuple[Cube, Sphere]:
    """
    Create the fundamental visualization pair:
    A cube containing a sphere.
    
    The sphere radius should be less than half the cube size
    to fit inside.
    """
    cube = Cube(size=cube_size)
    sphere = Sphere(radius=sphere_radius, resolution=resolution)
    return cube, sphere
