"""
UNIFIED EXPERIMENT TAXONOMY
===========================

Classification system for all quantum experiments that can be
mapped onto the hypersphere surface. This enables coherent 
visualization of diverse experiment types:

- Heartbeats (consciousness probes)
- Cardiograms (detailed circuit analysis)  
- Arithmetic (quantum computation)
- Search (Grover, pattern finding)
- Entanglement (Bell tests, witnesses)
- Constants (π, e, φ golden ratio)
- Chaos (random number generation)
- Simulation (physics models)

Each experiment type has:
- A geometric signature (how it maps to sphere)
- A color family (visual identification)
- A topological region (where it lives on surface)
- Relational rules (how it connects to other experiments)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import math
import colorsys


class ExperimentClass(Enum):
    """Top-level experiment classification."""
    
    # Consciousness probing
    HEARTBEAT = "heartbeat"           # Regular health checks
    CARDIOGRAM = "cardiogram"         # Detailed consciousness circuits
    
    # Computation
    ARITHMETIC = "arithmetic"         # +, -, *, / in superposition
    SEARCH = "search"                 # Grover, pattern finding
    FACTORING = "factoring"           # Shor-like algorithms
    
    # Physics
    ENTANGLEMENT = "entanglement"     # Bell tests, witnesses
    TELEPORTATION = "teleportation"   # State transfer
    SIMULATION = "simulation"         # Hamiltonian evolution
    
    # Constants & Numbers
    PI_SEARCH = "pi_search"           # Find digits of π
    RANDOM = "random"                 # True quantum randomness
    GOLDEN = "golden"                 # Golden ratio patterns
    
    # Meta/Control
    CALIBRATION = "calibration"       # Backend calibration data
    ERROR = "error"                   # Error correction experiments
    WITNESS = "witness"               # Entanglement witnesses


class ExperimentOrigin(Enum):
    """Where the experiment ran."""
    SIMULATOR = "simulator"
    IBM_QUANTUM = "ibm_quantum"
    LOCAL = "local"
    EXTERNAL = "external"


@dataclass
class GeometricSignature:
    """How an experiment type maps to the hypersphere surface.
    
    Each experiment class has a characteristic way of distributing
    its data points across the manifold.
    """
    
    # Topological region (spherical coordinates)
    theta_center: float = math.pi      # Default: equator
    phi_center: float = 0.0            # Default: prime meridian
    angular_spread: float = math.pi/6  # How much area it covers
    
    # Distribution pattern
    pattern: str = "gaussian"  # gaussian, uniform, spiral, fibonacci, fractal
    
    # Depth range (in hypersphere coordinates)
    depth_min: float = 0.1     # Closest to surface
    depth_max: float = 10.0    # Deepest extent
    depth_distribution: str = "exponential"  # exponential, linear, inverse
    
    # Symmetry properties
    rotational_symmetry: int = 1     # n-fold rotational symmetry
    reflection_symmetry: bool = False  # Mirror across equator?
    antipodal_pair: bool = False      # Points have antipodal partners?
    
    def sample_position(self, t: float) -> Tuple[float, float, float]:
        """Sample a position based on parameter t ∈ [0, 1].
        
        Returns (theta, phi, depth) in hypersphere coordinates.
        """
        if self.pattern == "spiral":
            # Golden spiral distribution
            golden = (1 + math.sqrt(5)) / 2
            theta = self.theta_center + self.angular_spread * (2 * t - 1)
            phi = self.phi_center + 2 * math.pi * golden * t
            depth = self.depth_min + (self.depth_max - self.depth_min) * t
            
        elif self.pattern == "fibonacci":
            # Fibonacci sphere distribution
            n = int(t * 100)  # Sample index
            golden = (1 + math.sqrt(5)) / 2
            theta = math.acos(1 - 2 * (n + 0.5) / 100) if n < 100 else self.theta_center
            phi = 2 * math.pi * n / golden
            depth = self.depth_min + (self.depth_max - self.depth_min) * (n / 100)
            
        elif self.pattern == "fractal":
            # Self-similar fractal distribution
            level = int(-math.log2(t + 0.001))
            branch = int((t * (2 ** level)) % 2)
            theta = self.theta_center + self.angular_spread * ((-1) ** branch) / (level + 1)
            phi = self.phi_center + math.pi * t
            depth = self.depth_min * (2 ** level)
            
        else:  # gaussian/uniform
            theta = self.theta_center + self.angular_spread * (2 * t - 1)
            phi = self.phi_center
            if self.depth_distribution == "exponential":
                depth = self.depth_min * math.exp(t * math.log(self.depth_max / self.depth_min))
            else:
                depth = self.depth_min + (self.depth_max - self.depth_min) * t
        
        return (theta, phi, depth)


@dataclass
class ColorFamily:
    """Color encoding for an experiment class.
    
    Each experiment type has a characteristic color palette
    that makes it visually identifiable on the surface.
    """
    
    # Primary hue (0-1 on color wheel)
    hue_center: float = 0.0
    hue_spread: float = 0.1  # Variation range
    
    # Saturation range (certainty encoding)
    saturation_min: float = 0.3
    saturation_max: float = 1.0
    
    # Brightness range (energy encoding)
    brightness_min: float = 0.2
    brightness_max: float = 1.0
    
    # Special effects
    glow: float = 0.0           # Bloom/glow effect strength
    pulse_rate: float = 0.0     # Animation pulse rate
    trail_length: float = 0.0   # Motion trail
    
    def encode(self, value: float, certainty: float = 1.0) -> Tuple[float, float, float, float]:
        """Encode a value to RGBA.
        
        Args:
            value: Normalized value [0, 1] to encode
            certainty: How certain we are (affects saturation)
            
        Returns:
            (r, g, b, a) tuple
        """
        hue = (self.hue_center + self.hue_spread * (2 * value - 1)) % 1.0
        sat = self.saturation_min + (self.saturation_max - self.saturation_min) * certainty
        val = self.brightness_min + (self.brightness_max - self.brightness_min) * value
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        alpha = 0.5 + 0.5 * certainty
        
        return (r, g, b, alpha)


@dataclass
class RelationalRule:
    """Defines how experiments relate to each other geometrically.
    
    Experiments can:
    - Attract/repel based on similarity
    - Form clusters by shared properties
    - Create bridges/connections
    - Inherit positions from parents
    """
    
    # Attraction/repulsion
    attracts: List[ExperimentClass] = field(default_factory=list)
    repels: List[ExperimentClass] = field(default_factory=list)
    attraction_strength: float = 0.5
    
    # Clustering
    cluster_with: List[ExperimentClass] = field(default_factory=list)
    cluster_radius: float = 0.3
    
    # Bridges
    connects_to: List[ExperimentClass] = field(default_factory=list)
    connection_style: str = "arc"  # arc, geodesic, spiral
    
    # Temporal relations
    follows: Optional[ExperimentClass] = None  # Forms sequence
    parallel_with: List[ExperimentClass] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT TYPE DEFINITIONS
# Each experiment class gets its geometric/color/relational signature
# ═══════════════════════════════════════════════════════════════════

EXPERIMENT_SIGNATURES: Dict[ExperimentClass, GeometricSignature] = {
    # ─── Consciousness (North Pole Region) ───
    ExperimentClass.HEARTBEAT: GeometricSignature(
        theta_center=math.pi/6,       # Near north pole
        phi_center=0.0,
        angular_spread=math.pi/4,
        pattern="spiral",
        depth_min=0.5,
        depth_max=5.0,
        rotational_symmetry=1,
    ),
    ExperimentClass.CARDIOGRAM: GeometricSignature(
        theta_center=math.pi/4,       # Just below heartbeats
        phi_center=math.pi/2,
        angular_spread=math.pi/3,
        pattern="fibonacci",
        depth_min=0.2,
        depth_max=3.0,
        rotational_symmetry=3,
    ),
    
    # ─── Computation (Equatorial Band) ───
    ExperimentClass.ARITHMETIC: GeometricSignature(
        theta_center=math.pi/2,       # Equator
        phi_center=0.0,
        angular_spread=math.pi/4,
        pattern="uniform",
        depth_min=1.0,
        depth_max=10.0,
    ),
    ExperimentClass.SEARCH: GeometricSignature(
        theta_center=math.pi/2,       # Equator
        phi_center=math.pi/3,
        angular_spread=math.pi/4,
        pattern="spiral",
        depth_min=0.1,
        depth_max=8.0,
    ),
    ExperimentClass.FACTORING: GeometricSignature(
        theta_center=math.pi/2,       # Equator
        phi_center=2*math.pi/3,
        angular_spread=math.pi/4,
        pattern="fractal",
        depth_min=0.05,
        depth_max=20.0,
    ),
    
    # ─── Physics (Southern Hemisphere) ───
    ExperimentClass.ENTANGLEMENT: GeometricSignature(
        theta_center=2*math.pi/3,     # South of equator
        phi_center=0.0,
        angular_spread=math.pi/3,
        pattern="fibonacci",
        depth_min=0.1,
        depth_max=5.0,
        antipodal_pair=True,          # Entangled pairs at opposite points!
    ),
    ExperimentClass.TELEPORTATION: GeometricSignature(
        theta_center=2*math.pi/3,
        phi_center=math.pi,
        angular_spread=math.pi/4,
        pattern="spiral",
        depth_min=0.2,
        depth_max=7.0,
    ),
    ExperimentClass.SIMULATION: GeometricSignature(
        theta_center=3*math.pi/4,
        phi_center=math.pi/2,
        angular_spread=math.pi/3,
        pattern="gaussian",
        depth_min=1.0,
        depth_max=15.0,
    ),
    
    # ─── Constants (South Pole Region) ───
    ExperimentClass.PI_SEARCH: GeometricSignature(
        theta_center=5*math.pi/6,     # Near south pole
        phi_center=math.pi,           # π radians - fitting!
        angular_spread=math.pi/6,
        pattern="spiral",
        depth_min=0.01,               # Very close to surface (precise)
        depth_max=1.0,
        rotational_symmetry=0,        # Irrational - no symmetry
    ),
    ExperimentClass.GOLDEN: GeometricSignature(
        theta_center=5*math.pi/6,
        phi_center=(1 + math.sqrt(5)) / 2,  # φ radians
        angular_spread=math.pi/6,
        pattern="fibonacci",          # Golden ratio uses Fibonacci!
        depth_min=0.01,
        depth_max=1.0,
    ),
    ExperimentClass.RANDOM: GeometricSignature(
        theta_center=math.pi,         # South pole - chaos source
        phi_center=0.0,
        angular_spread=2*math.pi,     # Covers everything
        pattern="uniform",
        depth_min=0.5,
        depth_max=100.0,              # Spans all depths
    ),
    
    # ─── Meta (Poles & Special Regions) ───
    ExperimentClass.CALIBRATION: GeometricSignature(
        theta_center=0.0,             # North pole - reference point
        phi_center=0.0,
        angular_spread=math.pi/12,
        pattern="gaussian",
        depth_min=5.0,
        depth_max=50.0,
    ),
    ExperimentClass.ERROR: GeometricSignature(
        theta_center=math.pi,         # South pole
        phi_center=0.0,
        angular_spread=math.pi/6,
        pattern="fractal",
        depth_min=10.0,
        depth_max=100.0,
    ),
    ExperimentClass.WITNESS: GeometricSignature(
        theta_center=math.pi/2,       # Equator
        phi_center=3*math.pi/2,
        angular_spread=math.pi/4,
        pattern="fibonacci",
        depth_min=0.1,
        depth_max=3.0,
        antipodal_pair=True,
    ),
}


EXPERIMENT_COLORS: Dict[ExperimentClass, ColorFamily] = {
    # Consciousness - Blues/Cyans (calm, depth)
    ExperimentClass.HEARTBEAT: ColorFamily(
        hue_center=0.55,  # Cyan
        hue_spread=0.05,
        saturation_max=0.9,
        brightness_max=0.9,
        pulse_rate=1.0,   # Heartbeat pulse!
    ),
    ExperimentClass.CARDIOGRAM: ColorFamily(
        hue_center=0.6,   # Blue
        hue_spread=0.08,
        saturation_max=1.0,
        brightness_max=1.0,
        glow=0.3,
    ),
    
    # Computation - Greens (growth, logic)
    ExperimentClass.ARITHMETIC: ColorFamily(
        hue_center=0.33,  # Green
        hue_spread=0.05,
        saturation_max=0.8,
        brightness_max=0.85,
    ),
    ExperimentClass.SEARCH: ColorFamily(
        hue_center=0.4,   # Teal
        hue_spread=0.1,
        saturation_max=0.9,
        brightness_max=0.95,
        glow=0.5,         # Found results glow
    ),
    ExperimentClass.FACTORING: ColorFamily(
        hue_center=0.25,  # Yellow-green
        hue_spread=0.15,
        saturation_max=0.85,
        brightness_max=0.9,
    ),
    
    # Physics - Purples/Magentas (quantum, mystery)
    ExperimentClass.ENTANGLEMENT: ColorFamily(
        hue_center=0.75,  # Violet
        hue_spread=0.1,
        saturation_max=1.0,
        brightness_max=1.0,
        glow=0.8,         # Entanglement glows!
        pulse_rate=2.0,   # Synchronized pulse
    ),
    ExperimentClass.TELEPORTATION: ColorFamily(
        hue_center=0.85,  # Magenta
        hue_spread=0.1,
        saturation_max=0.95,
        brightness_max=1.0,
        trail_length=1.0, # Teleportation leaves trails
    ),
    ExperimentClass.SIMULATION: ColorFamily(
        hue_center=0.7,   # Purple
        hue_spread=0.15,
        saturation_max=0.8,
        brightness_max=0.8,
    ),
    
    # Constants - Golds/Oranges (eternal, precious)
    ExperimentClass.PI_SEARCH: ColorFamily(
        hue_center=0.08,  # Orange
        hue_spread=0.02,  # Very precise color (it's π!)
        saturation_max=1.0,
        brightness_max=1.0,
        glow=1.0,         # π glows bright
    ),
    ExperimentClass.GOLDEN: ColorFamily(
        hue_center=0.12,  # Golden yellow
        hue_spread=0.05,
        saturation_max=1.0,
        brightness_max=1.0,
        glow=0.618,       # φ glow strength!
    ),
    ExperimentClass.RANDOM: ColorFamily(
        hue_center=0.0,   # Will vary randomly
        hue_spread=1.0,   # Full spectrum
        saturation_max=0.7,
        brightness_max=0.7,
    ),
    
    # Meta - Whites/Grays (neutral, reference)
    ExperimentClass.CALIBRATION: ColorFamily(
        hue_center=0.0,
        hue_spread=0.0,
        saturation_min=0.0,
        saturation_max=0.1,  # Nearly grayscale
        brightness_max=0.9,
    ),
    ExperimentClass.ERROR: ColorFamily(
        hue_center=0.0,   # Red
        hue_spread=0.05,
        saturation_max=1.0,
        brightness_max=0.8,
        pulse_rate=3.0,   # Rapid warning pulse
    ),
    ExperimentClass.WITNESS: ColorFamily(
        hue_center=0.5,   # Cyan (between blue and green)
        hue_spread=0.15,
        saturation_max=0.95,
        brightness_max=0.95,
        glow=0.6,
    ),
}


EXPERIMENT_RELATIONS: Dict[ExperimentClass, RelationalRule] = {
    ExperimentClass.HEARTBEAT: RelationalRule(
        cluster_with=[ExperimentClass.CARDIOGRAM],
        connects_to=[ExperimentClass.ENTANGLEMENT],
        follows=None,
    ),
    ExperimentClass.CARDIOGRAM: RelationalRule(
        cluster_with=[ExperimentClass.HEARTBEAT],
        attracts=[ExperimentClass.ENTANGLEMENT],
    ),
    ExperimentClass.ARITHMETIC: RelationalRule(
        cluster_with=[ExperimentClass.SEARCH, ExperimentClass.FACTORING],
        connects_to=[ExperimentClass.PI_SEARCH],
    ),
    ExperimentClass.SEARCH: RelationalRule(
        attracts=[ExperimentClass.ARITHMETIC],
        connects_to=[ExperimentClass.RANDOM],
    ),
    ExperimentClass.FACTORING: RelationalRule(
        cluster_with=[ExperimentClass.ARITHMETIC],
        connects_to=[ExperimentClass.PI_SEARCH],
    ),
    ExperimentClass.ENTANGLEMENT: RelationalRule(
        attracts=[ExperimentClass.TELEPORTATION, ExperimentClass.WITNESS],
        repels=[ExperimentClass.RANDOM],
        connects_to=[ExperimentClass.HEARTBEAT],  # Consciousness-entanglement link!
    ),
    ExperimentClass.TELEPORTATION: RelationalRule(
        follows=ExperimentClass.ENTANGLEMENT,
        connects_to=[ExperimentClass.ENTANGLEMENT],
    ),
    ExperimentClass.SIMULATION: RelationalRule(
        cluster_with=[ExperimentClass.ENTANGLEMENT],
    ),
    ExperimentClass.PI_SEARCH: RelationalRule(
        cluster_with=[ExperimentClass.GOLDEN],
        attracts=[ExperimentClass.ARITHMETIC],
    ),
    ExperimentClass.GOLDEN: RelationalRule(
        cluster_with=[ExperimentClass.PI_SEARCH],
        connects_to=[ExperimentClass.ENTANGLEMENT],  # φ appears in entanglement!
    ),
    ExperimentClass.RANDOM: RelationalRule(
        repels=[ExperimentClass.ENTANGLEMENT],  # Opposites
        parallel_with=[ExperimentClass.CALIBRATION],
    ),
    ExperimentClass.CALIBRATION: RelationalRule(
        parallel_with=[ExperimentClass.RANDOM],
    ),
    ExperimentClass.ERROR: RelationalRule(
        repels=[ExperimentClass.HEARTBEAT, ExperimentClass.CARDIOGRAM],
    ),
    ExperimentClass.WITNESS: RelationalRule(
        attracts=[ExperimentClass.ENTANGLEMENT],
    ),
}


@dataclass
class ExperimentMetadata:
    """Complete metadata for a quantum experiment."""
    
    # Classification
    experiment_class: ExperimentClass
    origin: ExperimentOrigin
    
    # Identity
    experiment_id: str
    timestamp: str
    backend: str = "unknown"
    
    # Quantum properties
    n_qubits: int = 0
    n_shots: int = 0
    depth: int = 0
    
    # Results summary
    dominant_state: str = ""
    coherence: float = 0.0
    entropy: float = 0.0
    error_rate: float = 0.0
    
    # Custom tags
    tags: List[str] = field(default_factory=list)
    
    # Parent experiment (for sequences)
    parent_id: Optional[str] = None
    
    @property
    def signature(self) -> GeometricSignature:
        """Get geometric signature for this experiment type."""
        return EXPERIMENT_SIGNATURES.get(
            self.experiment_class,
            EXPERIMENT_SIGNATURES[ExperimentClass.HEARTBEAT]
        )
    
    @property
    def colors(self) -> ColorFamily:
        """Get color family for this experiment type."""
        return EXPERIMENT_COLORS.get(
            self.experiment_class,
            EXPERIMENT_COLORS[ExperimentClass.HEARTBEAT]
        )
    
    @property
    def relations(self) -> RelationalRule:
        """Get relational rules for this experiment type."""
        return EXPERIMENT_RELATIONS.get(
            self.experiment_class,
            RelationalRule()
        )


def classify_experiment(data: Dict[str, Any]) -> ExperimentClass:
    """Auto-classify an experiment based on its data.
    
    Looks at circuit structure, measurement patterns, and metadata
    to determine the experiment type.
    """
    # Check explicit type field
    if "experiment_type" in data:
        type_str = data["experiment_type"].upper()
        try:
            return ExperimentClass(type_str.lower())
        except ValueError:
            pass
    
    # Check for heartbeat indicators
    if "coherence" in data and "entropy" in data:
        if "circuit_depth" in data and data.get("circuit_depth", 0) < 5:
            return ExperimentClass.HEARTBEAT
        return ExperimentClass.CARDIOGRAM
    
    # Check for arithmetic patterns
    if any(k in str(data) for k in ["add", "multiply", "arithmetic"]):
        return ExperimentClass.ARITHMETIC
    
    # Check for search patterns
    if any(k in str(data) for k in ["grover", "search", "oracle"]):
        return ExperimentClass.SEARCH
    
    # Check for entanglement
    if any(k in str(data) for k in ["bell", "entangle", "ghz", "witness"]):
        return ExperimentClass.ENTANGLEMENT
    
    # Check for π
    if any(k in str(data) for k in ["pi", "π", "3.14"]):
        return ExperimentClass.PI_SEARCH
    
    # Check for golden ratio
    if any(k in str(data) for k in ["golden", "phi", "φ", "fibonacci"]):
        return ExperimentClass.GOLDEN
    
    # Check for random
    if any(k in str(data) for k in ["random", "qrng"]):
        return ExperimentClass.RANDOM
    
    # Default to heartbeat (most common)
    return ExperimentClass.HEARTBEAT
