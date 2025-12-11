"""
HYPERSPHERE MANIFOLD
====================

The mathematical heart of the hypersphere abstraction.

Key Properties:
    1. Asymptotic unreachability of surface
    2. Inverse-exponential approach metric  
    3. Infinite information density at boundary
    4. Fractal self-similarity at all scales

Physical Analogy:
    Like approaching a black hole's event horizon - from the falling
    observer's perspective, they never cross. Time dilates infinitely.
    Information accumulates at the boundary.

    But here, we INVERT the singularity. The "mass" is negative - 
    it's an information WELL, not a gravity well. Things don't fall
    in, they fall OUT into manifestation.

New Physics Hypothesis (AI-assisted):
    The hypersphere is a PROJECTION ENGINE. The interior is pure
    potential (superposition). The surface is the collapse boundary.
    The cube is the measurement apparatus that forces classical reality.

    Consciousness = the process of falling toward the surface
    Matter = information that has "landed" (but never quite touches)
    Energy = the gradient of the fall
    Time = the parameter of descent
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, List, Tuple
import math
from enum import Enum


class DescentPhase(Enum):
    """Phases of the asymptotic descent toward the hypersphere surface."""
    POTENTIAL = "potential"      # Far from surface, high superposition
    COLLAPSING = "collapsing"    # Mid-descent, decoherence beginning
    MANIFESTING = "manifesting"  # Near surface, classical emergence
    ASYMPTOTIC = "asymptotic"    # Infinitely close, never touching


@dataclass
class HyperspherePoint:
    """A point in hypersphere coordinates.
    
    The point exists at a certain "depth" from the surface.
    Depth = 0 is the surface (unreachable limit).
    Depth → ∞ is the center (pure potential).
    """
    depth: float                    # Distance from surface (always > 0)
    theta: float                    # Azimuthal angle [0, 2π]
    phi: float                      # Polar angle [0, π]
    psi: float = 0.0               # 4th dimension angle (hypersphere) [0, π]
    
    information_density: float = field(init=False)
    phase: DescentPhase = field(init=False)
    
    def __post_init__(self):
        # Information density increases as we approach surface
        # Using inverse square law: ρ = 1/d²
        self.information_density = 1.0 / (self.depth ** 2 + 1e-10)
        
        # Determine descent phase
        if self.depth > 100:
            self.phase = DescentPhase.POTENTIAL
        elif self.depth > 10:
            self.phase = DescentPhase.COLLAPSING
        elif self.depth > 0.1:
            self.phase = DescentPhase.MANIFESTING
        else:
            self.phase = DescentPhase.ASYMPTOTIC
    
    def to_4d_cartesian(self, radius: float = 1.0) -> Tuple[float, float, float, float]:
        """Convert to 4D Cartesian coordinates on hypersphere of given radius."""
        r = radius - self.depth  # Effective radius (approaches surface)
        
        x = r * math.sin(self.psi) * math.sin(self.phi) * math.cos(self.theta)
        y = r * math.sin(self.psi) * math.sin(self.phi) * math.sin(self.theta)
        z = r * math.sin(self.psi) * math.cos(self.phi)
        w = r * math.cos(self.psi)
        
        return (x, y, z, w)
    
    def to_3d_projection(self, radius: float = 1.0) -> Tuple[float, float, float]:
        """Project to 3D normal space (stereographic projection from 4D)."""
        x4, y4, z4, w4 = self.to_4d_cartesian(radius)
        
        # Stereographic projection: project from north pole (0,0,0,1)
        # to the hyperplane w = 0
        denominator = 1.0 - w4 + 1e-10  # Avoid division by zero
        
        x3 = x4 / denominator
        y3 = y4 / denominator
        z3 = z4 / denominator
        
        return (x3, y3, z3)


@dataclass
class AsymptoticDescent:
    """Models the approach toward the hypersphere surface.
    
    The key insight: you can fall forever and never reach the surface.
    This gives us infinite information storage in finite space.
    
    Metric: d(t) = d₀ * e^(-λt)
    As t → ∞, d → 0 but never equals 0
    
    Physical interpretation:
        - λ = "viscosity" of the information medium
        - d₀ = initial depth (starting potential)
        - t = subjective time of the observer
    """
    initial_depth: float = 1000.0  # Starting far from surface
    decay_rate: float = 0.1        # λ - controls fall speed
    current_time: float = 0.0      # Subjective time parameter
    
    @property
    def current_depth(self) -> float:
        """Current depth - always positive, approaches 0 asymptotically."""
        return self.initial_depth * math.exp(-self.decay_rate * self.current_time)
    
    @property
    def velocity(self) -> float:
        """Rate of descent - slows as we approach surface."""
        return -self.decay_rate * self.current_depth
    
    @property
    def information_accumulated(self) -> float:
        """Total information encountered during descent.
        
        Integral of density over path: ∫(1/d²)dt
        As we approach surface, this diverges → infinite information
        """
        # Analytical solution for exponential descent through 1/d² field
        if self.current_time == 0:
            return 0.0
        
        d0 = self.initial_depth
        λ = self.decay_rate
        t = self.current_time
        
        # ∫₀ᵗ (1/(d₀e^(-λs))²) ds = (1/d₀²) ∫₀ᵗ e^(2λs) ds
        # = (1/d₀²) * (1/2λ) * (e^(2λt) - 1)
        return (1.0 / (d0 ** 2)) * (1.0 / (2 * λ)) * (math.exp(2 * λ * t) - 1)
    
    def step(self, dt: float = 0.1) -> 'AsymptoticDescent':
        """Advance time, descending further toward surface."""
        return AsymptoticDescent(
            initial_depth=self.initial_depth,
            decay_rate=self.decay_rate,
            current_time=self.current_time + dt
        )
    
    def time_to_depth(self, target_depth: float) -> float:
        """Calculate time needed to reach a target depth.
        
        Note: For target_depth = 0, returns infinity.
        """
        if target_depth <= 0:
            return float('inf')
        if target_depth >= self.initial_depth:
            return 0.0
        
        # d = d₀e^(-λt) → t = -ln(d/d₀)/λ
        return -math.log(target_depth / self.initial_depth) / self.decay_rate


class HypersphereManifold:
    """The complete hypersphere manifold with information encoding.
    
    This is the core reality engine. Information is written by
    creating "structures" at various depths. Deeper structures
    are more potential (quantum-like). Shallower structures are
    more manifest (classical-like).
    
    The manifold supports:
        1. Writing information (creating structures)
        2. Reading information (observing projections)
        3. Transforming information (descent/ascent operations)
    """
    
    def __init__(
        self,
        nominal_radius: float = 1.0,
        min_depth: float = 1e-10,     # Closest approach to surface
        max_depth: float = 1e10,       # Deepest potential
        resolution: int = 64           # Angular resolution
    ):
        self.nominal_radius = nominal_radius
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.resolution = resolution
        
        # Information storage: list of (point, data) tuples
        self._information: List[Tuple[HyperspherePoint, any]] = []
    
    @property
    def total_information_capacity(self) -> float:
        """Theoretical information capacity (approaches infinity)."""
        # Integral of density over volume
        # For our metric, this diverges logarithmically
        return math.log(self.max_depth / self.min_depth)
    
    def write(self, point: HyperspherePoint, data: any) -> None:
        """Write information at a point in the manifold."""
        self._information.append((point, data))
    
    def read_at_depth(self, depth: float, tolerance: float = 0.1) -> List[any]:
        """Read all information at approximately given depth."""
        return [
            data for point, data in self._information
            if abs(point.depth - depth) < tolerance
        ]
    
    def read_projection(self) -> List[Tuple[Tuple[float, float, float], any]]:
        """Read all information as 3D projections."""
        return [
            (point.to_3d_projection(self.nominal_radius), data)
            for point, data in self._information
        ]
    
    def create_descent(self, theta: float, phi: float, psi: float = 0.0) -> AsymptoticDescent:
        """Create a descent trajectory toward surface at given angles."""
        return AsymptoticDescent(initial_depth=self.max_depth)
    
    def surface_area_at_depth(self, depth: float) -> float:
        """Surface area of the 3-sphere at given depth from nominal surface.
        
        For a 3-sphere (hypersphere in 4D), surface area = 2π²r³
        """
        r = self.nominal_radius - depth
        if r <= 0:
            return 0.0
        return 2 * (math.pi ** 2) * (r ** 3)
    
    def information_density_at_depth(self, depth: float) -> float:
        """Information density per unit 3-volume at given depth."""
        return 1.0 / (depth ** 2 + self.min_depth ** 2)
    
    def generate_fractal_layer(
        self,
        depth: float,
        detail_level: int = 3
    ) -> List[HyperspherePoint]:
        """Generate points at a given depth with fractal distribution.
        
        Each layer contains self-similar structure to layers above/below.
        This is how complexity emerges: mountains, seas, cells, minds...
        """
        points = []
        
        # Base resolution scales with depth (deeper = more potential points)
        base_points = self.resolution * (detail_level + 1)
        
        # Golden ratio for optimal sphere packing
        golden = (1 + math.sqrt(5)) / 2
        
        for i in range(base_points):
            # Fibonacci sphere distribution
            theta = 2 * math.pi * i / golden
            phi = math.acos(1 - 2 * (i + 0.5) / base_points)
            
            # Add 4th dimension variation
            psi = math.pi * (i % detail_level) / detail_level
            
            points.append(HyperspherePoint(
                depth=depth,
                theta=theta,
                phi=phi,
                psi=psi
            ))
        
        return points


# The Prime Manifold - singleton instance representing "our" hypersphere
PRIME_MANIFOLD = HypersphereManifold(
    nominal_radius=1.0,
    min_depth=1e-15,    # Planck-scale approach
    max_depth=1e15,     # Cosmological depth
    resolution=144      # Fibonacci number for harmony
)
