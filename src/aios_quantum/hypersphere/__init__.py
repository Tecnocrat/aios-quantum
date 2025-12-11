"""
HYPERSPHERE MODULE
==================

"Ceci n'est pas une sphère" - This is not a sphere.

The visualization you see is a 3D normal-space proxy of a hyperspherical
information manifold. The true hypersphere cannot be rendered - only
approached asymptotically.

CORE INSIGHT:
    As resolution approaches infinity, the observer discovers they can
    NEVER reach the surface. This provides infinite information density
    in finite apparent volume.

MATHEMATICAL FOUNDATION:
    - The "sphere" is actually an inverse-exponential descent manifold
    - Distance to surface: d(t) = d₀ * e^(-λt) → never reaches 0
    - Information density: ρ(r) = ρ₀ / (R - r)² → ∞ as r → R
    - The cube is the minimal bosonic container for reality projection

TOPOLOGY:
    - Hypersphere interior: Infinite fractal depth (information space)
    - Cube walls: Read/write membrane (reality interface)
    - Cube exterior: Anti-space (conjugate information domain)

From this primitive, all complex structures emerge:
    Mountains → Seas → Cells → Humans → Machines → ???

The evolution continues.
"""

from .manifold import HypersphereManifold, AsymptoticDescent
from .membrane import CubeMembrane, InformationFlux
from .encoding import FractalEncoder, InverseExponentialMetric

__all__ = [
    'HypersphereManifold',
    'AsymptoticDescent',
    'CubeMembrane',
    'InformationFlux',
    'FractalEncoder',
    'InverseExponentialMetric',
]
