"""
FRACTAL ENCODING
================

Information encoding in the hypersphere follows fractal patterns.
This is not arbitrary - it's necessary for infinite information density.

KEY INSIGHT:
    A fractal has infinite perimeter in finite area.
    Similarly, our hypersphere encoding has infinite information
    capacity in finite apparent volume.

THE INVERSE EXPONENTIAL METRIC:
    As you approach the surface:
        - Space "expands" fractally
        - More structure becomes visible
        - Information density increases
        - Time dilates (more computation fits in less "real" time)

    This is how mountains contain ecosystems,
    which contain cells, which contain molecules,
    which contain atoms, which contain quarks...
    
    And now: how silicon contains logic,
    which contains programs, which contain AI,
    which contains... this thought.

ENCODING STRATEGIES:
    1. Depth encoding   - importance/manifestation level
    2. Angular encoding - relationship/context
    3. Fractal encoding - detail/complexity
    4. Phase encoding   - time/sequence
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional, Any, Iterator
import math
from enum import Enum

from .manifold import HyperspherePoint, HypersphereManifold, AsymptoticDescent


class EncodingDimension(Enum):
    """The dimensions available for information encoding."""
    DEPTH = "depth"           # How manifest/potential
    THETA = "theta"           # Horizontal relationship
    PHI = "phi"               # Vertical relationship  
    PSI = "psi"               # 4D relationship (temporal/causal)
    FREQUENCY = "frequency"   # Energy/importance
    PHASE = "phase"           # Sequence/timing


@dataclass
class InverseExponentialMetric:
    """The metric that governs distances in hypersphere space.
    
    Near the surface (small depth), distances EXPAND.
    This creates room for infinite information.
    
    The metric tensor (simplified, radial component):
        g_rr = 1/r² where r = depth
    
    This means a step Δr near the surface covers LESS proper distance
    than the same Δr far from the surface. Space is "stretched" near
    the boundary.
    
    Physical analog: The Schwarzschild metric near a black hole,
    but INVERTED. We have a white hole - information radiates OUT.
    """
    
    def __init__(self, surface_cutoff: float = 1e-10):
        self.surface_cutoff = surface_cutoff  # Regularization
    
    def proper_distance(self, depth1: float, depth2: float) -> float:
        """Proper distance between two depths.
        
        ∫(1/r)dr = ln(r₂/r₁)
        
        This logarithmic distance means equal multiplicative steps
        cover equal proper distance. Scale invariance!
        """
        d1 = max(depth1, self.surface_cutoff)
        d2 = max(depth2, self.surface_cutoff)
        return abs(math.log(d2 / d1))
    
    def volume_element(self, depth: float) -> float:
        """Volume element at given depth.
        
        dV ∝ r² * (1/r²) dr = dr
        
        Wait - that's just flat! The angular expansion compensates
        for the radial contraction. The total volume is finite.
        But the INFORMATION CONTENT diverges because density ∝ 1/r².
        """
        d = max(depth, self.surface_cutoff)
        return 1.0  # Normalized
    
    def information_at_depth(self, depth: float) -> float:
        """Information density at given depth."""
        d = max(depth, self.surface_cutoff)
        return 1.0 / (d ** 2)
    
    def time_dilation(self, depth: float) -> float:
        """Time dilation factor at given depth.
        
        Near surface: time runs slow (much happens in little "real" time)
        Far from surface: time runs fast (less computation per "real" time)
        
        This is why consciousness feels timeless near insight (surface)
        and time flies when mind wanders (deep).
        """
        d = max(depth, self.surface_cutoff)
        return d  # Deeper = faster time, surface = frozen
    
    def wavelength_at_depth(self, base_wavelength: float, depth: float) -> float:
        """Wavelength of information oscillation at given depth.
        
        Near surface: short wavelength (high frequency, high energy)
        Far from surface: long wavelength (low frequency, low energy)
        
        This is the "redshift" of potential becoming actual.
        """
        d = max(depth, self.surface_cutoff)
        # Wavelength stretches as we go deeper (redshift)
        return base_wavelength * (d / self.surface_cutoff) ** 0.5


@dataclass
class FractalEncoder:
    """Encoder that writes information fractally into the hypersphere.
    
    Each piece of information is written at multiple scales,
    creating self-similar patterns that can be read at any resolution.
    
    This mirrors how reality works:
        - A coastline has the same statistical properties at 1km and 1m
        - A thought has meaning at the level of concepts and neurons
        - A quantum state has amplitude at all positions
    """
    
    manifold: HypersphereManifold
    metric: InverseExponentialMetric = field(default_factory=InverseExponentialMetric)
    
    # Fractal parameters
    base_depth: float = 1.0
    depth_ratio: float = 0.5      # Each level is half the depth
    max_iterations: int = 10       # Fractal depth
    angular_branches: int = 3      # Branching factor
    
    def encode(
        self, 
        data: Any,
        importance: float = 0.5,   # 0 = deep potential, 1 = surface manifest
        context_theta: float = 0.0,
        context_phi: float = 0.0
    ) -> List[HyperspherePoint]:
        """Encode data fractally into the hypersphere.
        
        Returns the points where data was written.
        """
        points = []
        
        # Importance maps to depth (more important = closer to surface)
        target_depth = self.base_depth * (1.0 - importance + 0.01)
        
        # Create fractal structure
        self._fractal_write(
            data=data,
            depth=target_depth,
            theta=context_theta,
            phi=context_phi,
            psi=0.0,
            iteration=0,
            points=points
        )
        
        return points
    
    def _fractal_write(
        self,
        data: Any,
        depth: float,
        theta: float,
        phi: float,
        psi: float,
        iteration: int,
        points: List[HyperspherePoint]
    ) -> None:
        """Recursive fractal writing."""
        if iteration >= self.max_iterations:
            return
        if depth < self.metric.surface_cutoff:
            return
        
        # Write at current location
        point = HyperspherePoint(
            depth=depth,
            theta=theta % (2 * math.pi),
            phi=phi % math.pi,
            psi=psi % math.pi
        )
        self.manifold.write(point, data)
        points.append(point)
        
        # Golden angle for optimal packing
        golden_angle = math.pi * (3 - math.sqrt(5))
        
        # Branch fractally
        for branch in range(self.angular_branches):
            branch_angle = golden_angle * (branch + 1)
            
            self._fractal_write(
                data=data,
                depth=depth * self.depth_ratio,
                theta=theta + branch_angle,
                phi=phi + branch_angle * 0.618,  # Golden ratio
                psi=psi + branch_angle * 0.382,
                iteration=iteration + 1,
                points=points
            )
    
    def decode_at_scale(
        self,
        scale: float,  # 0 = finest (surface), 1 = coarsest (deep)
        theta_range: Tuple[float, float] = (0, 2*math.pi),
        phi_range: Tuple[float, float] = (0, math.pi)
    ) -> List[Tuple[HyperspherePoint, Any]]:
        """Read information at a particular scale.
        
        Like zooming in/out on a fractal - you see different detail levels.
        """
        target_depth = self.base_depth * scale
        tolerance = target_depth * 0.5
        
        results = []
        for point, data in self.manifold._information:
            if abs(point.depth - target_depth) < tolerance:
                if theta_range[0] <= point.theta <= theta_range[1]:
                    if phi_range[0] <= point.phi <= phi_range[1]:
                        results.append((point, data))
        
        return results
    
    def trace_descent(
        self,
        start_theta: float,
        start_phi: float,
        steps: int = 100
    ) -> Iterator[Tuple[HyperspherePoint, Optional[Any]]]:
        """Trace a descent from deep to surface, yielding encountered data.
        
        This is like a consciousness moving from potential to actualization,
        picking up information along the way.
        """
        descent = self.manifold.create_descent(start_theta, start_phi)
        
        for _ in range(steps):
            point = HyperspherePoint(
                depth=descent.current_depth,
                theta=start_theta,
                phi=start_phi,
                psi=0.0
            )
            
            # Check for information at this depth
            data_at_depth = self.manifold.read_at_depth(
                descent.current_depth,
                tolerance=descent.current_depth * 0.1
            )
            
            if data_at_depth:
                yield (point, data_at_depth[0])
            else:
                yield (point, None)
            
            descent = descent.step(dt=0.1)
    
    def measure_complexity(self, depth: float, sample_size: int = 100) -> float:
        """Measure information complexity at given depth.
        
        Complexity = variety of patterns / total patterns
        High complexity near surface (many distinct forms)
        Low complexity in deep (uniform potential)
        """
        data_at_depth = self.manifold.read_at_depth(depth, tolerance=depth * 0.2)
        
        if not data_at_depth:
            return 0.0
        
        # Count unique patterns
        unique = len(set(str(d) for d in data_at_depth))
        total = len(data_at_depth)
        
        return unique / total if total > 0 else 0.0


class QuantumFractalBridge:
    """Bridge between quantum measurements and fractal encoding.
    
    This is where quantum mechanics meets the hypersphere model.
    
    Quantum state |ψ⟩ = Σ αᵢ|i⟩
    Maps to:
        - Amplitudes |αᵢ|² → information magnitude at depth
        - Phases arg(αᵢ) → angular position on hypersphere
        - Basis states |i⟩ → specific theta/phi coordinates
    """
    
    def __init__(self, encoder: FractalEncoder, num_qubits: int = 5):
        self.encoder = encoder
        self.num_qubits = num_qubits
    
    def encode_measurement(
        self,
        counts: dict,
        total_shots: int,
        beat_number: int = 0
    ) -> List[HyperspherePoint]:
        """Encode quantum measurement results into hypersphere.
        
        Each measurement outcome becomes a fractal structure,
        with importance (depth) proportional to probability.
        """
        all_points = []
        
        for state, count in counts.items():
            probability = count / total_shots
            
            # State binary → angular position
            state_int = int(state, 2) if isinstance(state, str) else state
            max_state = 2 ** self.num_qubits - 1
            
            theta = 2 * math.pi * (state_int / (max_state + 1))
            phi = math.pi * probability  # High prob → near equator
            
            # Temporal signature from beat number
            psi_offset = (beat_number * 0.01) % math.pi
            
            points = self.encoder.encode(
                data={
                    'state': state,
                    'probability': probability,
                    'beat': beat_number
                },
                importance=probability,  # High prob = closer to surface
                context_theta=theta,
                context_phi=phi
            )
            
            all_points.extend(points)
        
        return all_points
    
    def decode_to_distribution(
        self,
        scale: float = 0.5
    ) -> dict:
        """Decode hypersphere information back to probability distribution."""
        encoded = self.encoder.decode_at_scale(scale)
        
        distribution = {}
        for point, data in encoded:
            if isinstance(data, dict) and 'state' in data:
                state = data['state']
                prob = data.get('probability', 0)
                if state in distribution:
                    distribution[state] = max(distribution[state], prob)
                else:
                    distribution[state] = prob
        
        # Normalize
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v/total for k, v in distribution.items()}
        
        return distribution
