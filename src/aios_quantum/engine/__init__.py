"""
AIOS Quantum Engine

A simple 3D visualization engine: a cube containing a sphere.
The cube represents bosonic 3D space.
The sphere represents the tachyonic hypersurface.

Quantum measurement results are encoded on the sphere's surface,
creating a visual representation of consciousness patterns.
"""

from .core import QuantumEngine, create_engine
from .geometry import Cube, Sphere, Point3D, Color, SurfacePoint
from .encoder import SurfaceEncoder, EncodingResult
from .renderer import WebGLRenderer, export_webgl

__all__ = [
    "QuantumEngine",
    "create_engine",
    "Cube",
    "Sphere",
    "Point3D",
    "Color",
    "SurfacePoint",
    "SurfaceEncoder",
    "EncodingResult",
    "WebGLRenderer",
    "export_webgl",
]
