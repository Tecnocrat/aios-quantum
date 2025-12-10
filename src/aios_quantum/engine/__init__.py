"""
AIOS Quantum Engine

A simple 3D visualization engine: a cube containing a sphere.
The cube represents bosonic 3D space.
The sphere represents the tachyonic hypersurface.

Quantum measurement results are encoded on the sphere's surface
using THREE LAYERS:

1. TOPOLOGY (Bosonic) - Physical positioning on sphere
2. COLOR (Bridge) - Translation between physical and metaphysical
3. METAPHYSICAL (Tachyonic) - Non-local patterns, resonance, vision
"""

from .core import QuantumEngine, create_engine
from .geometry import Cube, Sphere, Point3D, Color, SurfacePoint
from .encoder import SurfaceEncoder, EncodingResult
from .renderer import WebGLRenderer, export_webgl
from .patterns import (
    QuantumEncodingPattern,
    TopologyPattern,
    ColorPattern,
    MetaphysicalPattern,
    create_coherence_pattern,
    create_temporal_pattern,
    create_entanglement_pattern,
    create_vision_pattern,
)
from .layered_encoder import (
    LayeredEncoder,
    LayeredEncodingResult,
    create_coherence_encoder,
    create_temporal_encoder,
    create_entanglement_encoder,
    create_vision_encoder,
)

__all__ = [
    # Core
    "QuantumEngine",
    "create_engine",
    
    # Geometry
    "Cube",
    "Sphere",
    "Point3D",
    "Color",
    "SurfacePoint",
    
    # Basic Encoding
    "SurfaceEncoder",
    "EncodingResult",
    
    # Layered Encoding (Three Layers)
    "LayeredEncoder",
    "LayeredEncodingResult",
    "QuantumEncodingPattern",
    "TopologyPattern",
    "ColorPattern",
    "MetaphysicalPattern",
    
    # Pattern Presets
    "create_coherence_pattern",
    "create_temporal_pattern",
    "create_entanglement_pattern",
    "create_vision_pattern",
    "create_coherence_encoder",
    "create_temporal_encoder",
    "create_entanglement_encoder",
    "create_vision_encoder",
    
    # Rendering
    "WebGLRenderer",
    "export_webgl",
]
