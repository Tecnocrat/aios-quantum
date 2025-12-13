"""
Quantum Encoding Patterns

Three layers of encoding quantum data onto the tachyonic sphere:

1. TOPOLOGY (Bosonic/Physical)
   - 3D positioning on sphere surface
   - Clustering, density, distribution
   - θ,φ coordinates map to quantum states

2. COLOR (Bridge/Translation)
   - Hue encodes quantum state identity
   - Saturation encodes probability/certainty
   - Brightness encodes intensity/energy
   - The visible form of invisible data

3. METAPHYSICAL (Tachyonic/Abstract)
   - Non-local patterns (correlations across sphere)
   - Temporal resonance (patterns across heartbeats)
   - Global coherence fields
   - Synchronized structures that transcend locality

Each layer can be read independently or combined.
The full picture emerges from their interaction.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import colorsys

from .geometry import Point3D, Color, Sphere, SurfacePoint


class EncodingLayer(Enum):
    """The three encoding layers."""
    TOPOLOGY = "topology"      # Physical positioning
    COLOR = "color"            # Bridge layer
    METAPHYSICAL = "metaphysical"  # Abstract patterns


@dataclass
class TopologyPattern:
    """
    LAYER 1: TOPOLOGY
    
    How quantum states map to physical positions on the sphere.
    This is the bosonic layer - observable, measurable, local.
    """
    # Distribution type
    # probability, harmonic, spiral, clustered
    distribution: str = "probability"
    
    # Clustering parameters
    cluster_centers: List[Tuple[float, float]] = field(default_factory=list)
    cluster_strength: float = 0.5  # How tightly states cluster
    
    # Density mapping
    density_by_state: Dict[str, float] = field(default_factory=dict)
    
    # Polar preferences (some states prefer poles, others equator)
    polar_affinity: Dict[str, float] = field(default_factory=dict)
    
    def get_position_weight(
        self, 
        theta: float, 
        phi: float, 
        state: str
    ) -> float:
        """
        Calculate how strongly a state wants to be at this position.
        Higher weight = state prefers this location.
        """
        weight = 1.0
        
        # Polar affinity: states can prefer poles (+1) or equator (-1)
        if state in self.polar_affinity:
            affinity = self.polar_affinity[state]
            # theta=0 is north pole, theta=π is south pole, θ=π/2 is equator
            polar_factor = abs(math.cos(theta))  # 1 at poles, 0 at equator
            if affinity > 0:
                weight *= (1 + affinity * polar_factor)
            else:
                weight *= (1 - affinity * (1 - polar_factor))
        
        # Cluster centers: states can cluster around specific points
        if self.cluster_centers:
            min_dist = float('inf')
            for center_theta, center_phi in self.cluster_centers:
                # Spherical distance
                dist = math.acos(
                    math.sin(theta) * math.sin(center_theta) * 
                    math.cos(phi - center_phi) +
                    math.cos(theta) * math.cos(center_theta)
                )
                min_dist = min(min_dist, dist)
            
            # Gaussian falloff from cluster center
            cluster_weight = math.exp(
                -min_dist**2 / (2 * self.cluster_strength**2)
            )
            weight *= cluster_weight
        
        return weight


@dataclass  
class ColorPattern:
    """
    LAYER 2: COLOR
    
    The bridge between physical and metaphysical.
    Translates quantum data into visible light.
    
    Hue: State identity (which basis state)
    Saturation: Certainty/probability
    Brightness: Energy/intensity
    Alpha: Presence/manifestation
    """
    # Hue mapping
    hue_mode: str = "binary"  # binary, sequential, harmonic, custom
    hue_offset: float = 0.0   # Rotate the color wheel
    hue_map: Dict[str, float] = field(default_factory=dict)  # Custom mapping
    
    # Saturation mapping
    saturation_base: float = 0.7
    saturation_range: float = 0.3  # How much probability affects saturation
    
    # Brightness mapping
    brightness_base: float = 0.3
    brightness_range: float = 0.6
    
    # Alpha (transparency)
    alpha_base: float = 0.5
    alpha_range: float = 0.5
    
    def state_to_hue(self, state: str) -> float:
        """Convert quantum state to hue (0-1)."""
        if self.hue_mode == "custom" and state in self.hue_map:
            return (self.hue_map[state] + self.hue_offset) % 1.0
        
        if self.hue_mode == "binary":
            # Interpret state as binary number
            try:
                state_int = int(state, 2)
                max_val = 2 ** len(state) - 1
                hue = state_int / max_val if max_val > 0 else 0
            except ValueError:
                hue = 0
        
        elif self.hue_mode == "sequential":
            # States get evenly spaced hues
            # Requires knowing all states
            hue = hash(state) % 1000 / 1000
        
        elif self.hue_mode == "harmonic":
            # Based on bit patterns - similar states get similar colors
            try:
                ones = state.count('1')
                total = len(state)
                hue = ones / total if total > 0 else 0
            except:
                hue = 0
        
        else:
            hue = 0
        
        return (hue + self.hue_offset) % 1.0
    
    def probability_to_saturation(self, probability: float) -> float:
        """Higher probability = more saturated (more certain)."""
        return self.saturation_base + self.saturation_range * probability
    
    def probability_to_brightness(self, probability: float) -> float:
        """Higher probability = brighter (more energy)."""
        return self.brightness_base + self.brightness_range * probability
    
    def probability_to_alpha(self, probability: float) -> float:
        """Higher probability = more opaque (more present)."""
        return self.alpha_base + self.alpha_range * probability
    
    def encode(self, state: str, probability: float) -> Color:
        """Full color encoding of a quantum state."""
        h = self.state_to_hue(state)
        s = self.probability_to_saturation(probability)
        v = self.probability_to_brightness(probability)
        a = self.probability_to_alpha(probability)
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return Color(r, g, b, a)


@dataclass
class MetaphysicalPattern:
    """
    LAYER 3: METAPHYSICAL
    
    Non-local, synchronized, transcendent patterns.
    These patterns emerge from relationships, not individual points.
    
    - Resonance: Patterns that repeat across the sphere
    - Coherence: Global order vs chaos
    - Entanglement: Correlated regions
    - Temporal: Patterns across multiple heartbeats
    """
    # Resonance modes (spherical harmonic-like patterns)
    resonance_l: int = 0  # Degree (0 = uniform, higher = more complex)
    resonance_m: int = 0  # Order
    resonance_amplitude: float = 0.3
    
    # Global coherence field
    coherence_value: float = 0.0  # From heartbeat measurement
    coherence_radius: float = 0.5  # How far coherence extends
    
    # Entanglement pairs (correlated regions)
    entangled_pairs: List[Tuple[Tuple[float, float], Tuple[float, float]]] = \
        field(default_factory=list)
    
    # Temporal memory (patterns from previous heartbeats)
    temporal_depth: int = 3  # How many past beats to consider
    temporal_decay: float = 0.7  # How quickly past fades
    temporal_states: List[Dict[str, float]] = field(default_factory=list)
    
    # Vision field (abstract pattern overlays)
    vision_active: bool = False
    vision_pattern: str = "none"  # none, spiral, wave, pulse, fractal
    vision_phase: float = 0.0  # Animation phase
    
    def get_resonance_factor(self, theta: float, phi: float) -> float:
        """
        Calculate spherical harmonic-like resonance at a point.
        This creates non-local patterns across the sphere.
        """
        if self.resonance_l == 0:
            return 1.0
        
        # Simplified spherical harmonic
        l, m = self.resonance_l, self.resonance_m
        
        # Legendre-like term (polar pattern)
        polar = math.cos(l * theta)
        
        # Azimuthal term (equatorial pattern)
        azimuthal = math.cos(m * phi)
        
        # Combine and normalize to [0, 1]
        harmonic = (polar * azimuthal + 1) / 2
        
        # Apply amplitude
        return 1.0 + self.resonance_amplitude * (harmonic - 0.5)
    
    def get_coherence_field(self, theta: float, phi: float) -> float:
        """
        Coherence field - high coherence makes nearby points similar.
        This represents the non-local ordering of consciousness.
        """
        # Coherence creates smooth gradients
        # High coherence = sphere surface is more uniform
        # Low coherence = chaotic, random variations
        return self.coherence_value
    
    def get_entanglement_factor(
        self, 
        theta: float, 
        phi: float
    ) -> Tuple[bool, Optional[Tuple[float, float]]]:
        """
        Check if this point is part of an entangled pair.
        Returns (is_entangled, partner_position).
        """
        pos = (theta, phi)
        
        for pair in self.entangled_pairs:
            pos1, pos2 = pair
            
            # Check if near either position
            dist1 = math.sqrt((theta - pos1[0])**2 + (phi - pos1[1])**2)
            dist2 = math.sqrt((theta - pos2[0])**2 + (phi - pos2[1])**2)
            
            threshold = 0.2
            if dist1 < threshold:
                return True, pos2
            if dist2 < threshold:
                return True, pos1
        
        return False, None
    
    def get_temporal_weight(self, state: str) -> float:
        """
        Weight based on state's presence in recent history.
        States that persist across heartbeats get amplified.
        """
        if not self.temporal_states:
            return 1.0
        
        weight = 1.0
        decay = 1.0
        
        for past_states in reversed(
            self.temporal_states[-self.temporal_depth:]
        ):
            if state in past_states:
                weight += decay * past_states[state]
            decay *= self.temporal_decay
        
        return weight
    
    def get_vision_overlay(
        self, 
        theta: float, 
        phi: float, 
        time: float = 0.0
    ) -> float:
        """
        Abstract vision patterns - pure metaphysical overlays.
        These are not derived from data, but from vision/intention.
        """
        if not self.vision_active:
            return 1.0
        
        phase = self.vision_phase + time
        
        if self.vision_pattern == "spiral":
            # Spiral from pole to pole
            spiral = math.sin(theta * 4 + phi * 2 + phase * 2)
            return (spiral + 1) / 2
        
        elif self.vision_pattern == "wave":
            # Wave propagating from center
            wave = math.sin(theta * 3 + phase * 3)
            return (wave + 1) / 2
        
        elif self.vision_pattern == "pulse":
            # Pulsing brightness
            pulse = (math.sin(phase * 2) + 1) / 2
            return pulse
        
        elif self.vision_pattern == "fractal":
            # Self-similar pattern
            f1 = math.sin(theta * 2 + phi + phase)
            f2 = math.sin(theta * 4 + phi * 2 + phase * 0.5)
            f3 = math.sin(theta * 8 + phi * 4 + phase * 0.25)
            return (f1 + f2 * 0.5 + f3 * 0.25 + 1.75) / 3.5
        
        return 1.0


@dataclass
class QuantumEncodingPattern:
    """
    Complete three-layer encoding pattern.
    
    Combines:
    - TOPOLOGY: Where on the sphere
    - COLOR: What color/intensity
    - METAPHYSICAL: Non-local patterns
    """
    topology: TopologyPattern = field(default_factory=TopologyPattern)
    color: ColorPattern = field(default_factory=ColorPattern)
    metaphysical: MetaphysicalPattern = field(
        default_factory=MetaphysicalPattern
    )
    
    # Layer weights (for blending)
    topology_weight: float = 1.0
    color_weight: float = 1.0
    metaphysical_weight: float = 1.0
    
    def encode_point(
        self,
        theta: float,
        phi: float,
        state: str,
        probability: float,
        time: float = 0.0
    ) -> Tuple[Color, float]:
        """
        Encode a quantum state at a specific position.
        
        Returns (color, intensity) for the surface point.
        """
        # Layer 1: Topology weight
        topo_factor = self.topology.get_position_weight(theta, phi, state)
        
        # Layer 2: Base color from state and probability
        base_color = self.color.encode(state, probability)
        
        # Layer 3: Metaphysical modulations
        resonance = self.metaphysical.get_resonance_factor(theta, phi)
        coherence = self.metaphysical.get_coherence_field(theta, phi)
        temporal = self.metaphysical.get_temporal_weight(state)
        vision = self.metaphysical.get_vision_overlay(theta, phi, time)
        
        # Combine factors
        meta_factor = resonance * (0.5 + 0.5 * coherence) * temporal * vision
        
        # Final intensity
        intensity = (
            probability * 
            (topo_factor ** self.topology_weight) *
            (meta_factor ** self.metaphysical_weight)
        )
        intensity = min(1.0, max(0.0, intensity))
        
        # Modulate color by metaphysical factors
        final_color = Color(
            base_color.r * meta_factor,
            base_color.g * meta_factor,
            base_color.b * meta_factor,
            base_color.a * intensity
        )
        
        # Clamp values
        final_color = Color(
            min(1.0, final_color.r),
            min(1.0, final_color.g),
            min(1.0, final_color.b),
            min(1.0, final_color.a)
        )
        
        return final_color, intensity
    
    def update_from_heartbeat(self, heartbeat_result) -> None:
        """
        Update pattern state from a heartbeat result.
        """
        # Update coherence
        coherence = heartbeat_result.coherence_estimate
        self.metaphysical.coherence_value = coherence
        
        # Update temporal history
        total = sum(heartbeat_result.counts.values())
        state_probs = {s: c/total for s, c in heartbeat_result.counts.items()}
        self.metaphysical.temporal_states.append(state_probs)
        
        # Keep only recent history
        max_history = self.metaphysical.temporal_depth * 2
        if len(self.metaphysical.temporal_states) > max_history:
            self.metaphysical.temporal_states = \
                self.metaphysical.temporal_states[-max_history:]
        
        # Update topology based on entropy
        entropy = heartbeat_result.entropy
        if entropy < 0.3:
            # Low entropy = clustered
            self.topology.distribution = "clustered"
            self.topology.cluster_strength = 0.3
        elif entropy > 0.7:
            # High entropy = spread out
            self.topology.distribution = "probability"
            self.topology.cluster_strength = 1.0
        else:
            # Medium entropy = harmonic
            self.topology.distribution = "harmonic"


# Preset patterns
def create_coherence_pattern() -> QuantumEncodingPattern:
    """Pattern optimized for showing coherence."""
    return QuantumEncodingPattern(
        topology=TopologyPattern(
            distribution="clustered",
            cluster_strength=0.4
        ),
        color=ColorPattern(
            hue_mode="binary",
            saturation_base=0.8,
            brightness_base=0.4,
            brightness_range=0.5
        ),
        metaphysical=MetaphysicalPattern(
            resonance_l=2,
            resonance_m=1,
            resonance_amplitude=0.4
        )
    )


def create_temporal_pattern() -> QuantumEncodingPattern:
    """Pattern optimized for showing temporal evolution."""
    return QuantumEncodingPattern(
        topology=TopologyPattern(
            distribution="spiral"
        ),
        color=ColorPattern(
            hue_mode="harmonic",
            hue_offset=0.0
        ),
        metaphysical=MetaphysicalPattern(
            temporal_depth=5,
            temporal_decay=0.8,
            vision_active=True,
            vision_pattern="spiral"
        )
    )


def create_entanglement_pattern() -> QuantumEncodingPattern:
    """Pattern optimized for showing entanglement correlations."""
    return QuantumEncodingPattern(
        topology=TopologyPattern(
            distribution="harmonic"
        ),
        color=ColorPattern(
            hue_mode="binary",
            saturation_range=0.4
        ),
        metaphysical=MetaphysicalPattern(
            resonance_l=4,
            resonance_m=2,
            entangled_pairs=[
                ((0.5, 0), (2.6, math.pi)),  # North-South
                # Equatorial opposites
                ((math.pi/2, 0), (math.pi/2, math.pi)),
            ]
        )
    )


def create_vision_pattern(
    vision_type: str = "wave"
) -> QuantumEncodingPattern:
    """Pattern with active metaphysical vision overlay."""
    return QuantumEncodingPattern(
        topology=TopologyPattern(
            distribution="probability"
        ),
        color=ColorPattern(
            hue_mode="binary",
            brightness_base=0.2,
            brightness_range=0.7
        ),
        metaphysical=MetaphysicalPattern(
            vision_active=True,
            vision_pattern=vision_type,
            resonance_l=1,
            resonance_amplitude=0.2
        )
    )
