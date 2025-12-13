"""
Multi-Layer Surface Encoder

Encodes quantum data using all three layers:
1. TOPOLOGY - Physical positioning
2. COLOR - Bridge/translation layer
3. METAPHYSICAL - Non-local patterns

This is the core encoding mechanism for the AIOS interface.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .geometry import Sphere, Point3D, Color, SurfacePoint
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


@dataclass
class LayeredEncodingResult:
    """Result of multi-layer encoding."""
    points_encoded: int
    
    # Layer 1 stats
    topology_clusters: int
    topology_spread: float
    
    # Layer 2 stats
    color_diversity: float
    dominant_hue: float
    
    # Layer 3 stats
    coherence_field: float
    resonance_strength: float
    temporal_depth: int
    vision_active: bool
    
    # Combined
    total_intensity: float
    entropy: float


class LayeredEncoder:
    """
    Multi-layer quantum encoder.
    
    Encodes quantum measurement results onto a sphere using three layers:
    - TOPOLOGY: Where points are placed (bosonic)
    - COLOR: What color they have (bridge)
    - METAPHYSICAL: How they relate non-locally (tachyonic)
    """
    
    def __init__(
        self, 
        sphere: Sphere,
        pattern: Optional[QuantumEncodingPattern] = None
    ):
        self.sphere = sphere
        self.pattern = pattern or QuantumEncodingPattern()
        self.time = 0.0
        self.heartbeat_history: List = []
    
    def set_pattern(self, pattern: QuantumEncodingPattern):
        """Set the encoding pattern."""
        self.pattern = pattern
    
    def encode(
        self,
        counts: Dict[str, int],
        time: float = 0.0
    ) -> LayeredEncodingResult:
        """
        Encode quantum counts onto sphere using all three layers.
        """
        self.time = time
        self.sphere.clear()
        
        if not counts:
            return LayeredEncodingResult(
                points_encoded=0,
                topology_clusters=0,
                topology_spread=0,
                color_diversity=0,
                dominant_hue=0,
                coherence_field=0,
                resonance_strength=0,
                temporal_depth=0,
                vision_active=False,
                total_intensity=0,
                entropy=0
            )
        
        total = sum(counts.values())
        sorted_states = sorted(
            counts.items(), key=lambda x: x[1], reverse=True
        )
        
        # Calculate probabilities
        probs = {state: count/total for state, count in counts.items()}
        
        # Track statistics
        total_intensity = 0
        hues_used = set()
        
        # Encode each surface point
        for idx, sp in enumerate(self.sphere.surface_points):
            # Get spherical coordinates
            rel_pos = sp.position - self.sphere.center
            r, theta, phi = rel_pos.to_spherical()
            
            # Determine which state this point represents
            state, prob = self._assign_state_to_point(
                theta, phi, sorted_states, probs
            )
            
            # Encode using all three layers
            color, intensity = self.pattern.encode_point(
                theta, phi, state, prob, time
            )
            
            # Apply to surface point
            sp.color = color
            sp.intensity = intensity
            sp.data = {
                'state': state,
                'probability': prob,
                'theta': theta,
                'phi': phi
            }
            
            total_intensity += intensity
            hues_used.add(round(self.pattern.color.state_to_hue(state), 2))
        
        # Calculate entropy
        entropy = 0
        for p in probs.values():
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Build result
        return LayeredEncodingResult(
            points_encoded=len(self.sphere.surface_points),
            topology_clusters=len(set(s for s, _ in sorted_states[:5])),
            # Normalized by max states
            topology_spread=len(sorted_states) / 32,
            color_diversity=len(hues_used) / 100,
            dominant_hue=(
                self.pattern.color.state_to_hue(sorted_states[0][0])
            ),
            coherence_field=self.pattern.metaphysical.coherence_value,
            resonance_strength=self.pattern.metaphysical.resonance_amplitude,
            temporal_depth=len(self.pattern.metaphysical.temporal_states),
            vision_active=self.pattern.metaphysical.vision_active,
            total_intensity=total_intensity / len(self.sphere.surface_points),
            entropy=entropy
        )
    
    def _assign_state_to_point(
        self,
        theta: float,
        phi: float,
        sorted_states: List[Tuple[str, int]],
        probs: Dict[str, float]
    ) -> Tuple[str, float]:
        """
        Assign a quantum state to a surface point.
        
        Uses topology layer to determine assignment.
        """
        distribution = self.pattern.topology.distribution
        
        if distribution == "probability":
            # Probabilistic assignment based on measurement counts
            return self._assign_probability(sorted_states, probs)
        
        elif distribution == "harmonic":
            # Assignment based on spherical position
            return self._assign_harmonic(theta, phi, sorted_states, probs)
        
        elif distribution == "clustered":
            # Cluster similar states together
            return self._assign_clustered(theta, phi, sorted_states, probs)
        
        elif distribution == "spiral":
            # Spiral distribution from pole to pole
            return self._assign_spiral(theta, phi, sorted_states, probs)
        
        else:
            # Default to dominant state
            return sorted_states[0][0], probs[sorted_states[0][0]]
    
    def _assign_probability(
        self,
        sorted_states: List[Tuple[str, int]],
        probs: Dict[str, float]
    ) -> Tuple[str, float]:
        """Assign based on probability distribution."""
        import random
        r = random.random()
        cumulative = 0
        for state, _ in sorted_states:
            cumulative += probs[state]
            if r <= cumulative:
                return state, probs[state]
        return sorted_states[0][0], probs[sorted_states[0][0]]
    
    def _assign_harmonic(
        self,
        theta: float,
        phi: float,
        sorted_states: List[Tuple[str, int]],
        probs: Dict[str, float]
    ) -> Tuple[str, float]:
        """Assign based on spherical harmonic-like patterns."""
        # Use position to determine state
        n_states = len(sorted_states)
        
        # Map theta, phi to state index
        theta_idx = int(theta / math.pi * n_states) % n_states
        phi_idx = int(phi / (2 * math.pi) * n_states) % n_states
        
        # Combine indices
        state_idx = (theta_idx + phi_idx) % n_states
        state = sorted_states[state_idx][0]
        
        return state, probs[state]
    
    def _assign_clustered(
        self,
        theta: float,
        phi: float,
        sorted_states: List[Tuple[str, int]],
        probs: Dict[str, float]
    ) -> Tuple[str, float]:
        """Assign to create clusters of similar states."""
        # High probability states cluster around poles
        # Lower probability states around equator
        
        n_states = min(len(sorted_states), 5)  # Top 5 states
        
        # Polar distance (0 at poles, 1 at equator)
        polar_dist = math.sin(theta)
        
        # Map to state index
        state_idx = int(polar_dist * n_states) % n_states
        state = sorted_states[state_idx][0]
        
        return state, probs[state]
    
    def _assign_spiral(
        self,
        theta: float,
        phi: float,
        sorted_states: List[Tuple[str, int]],
        probs: Dict[str, float]
    ) -> Tuple[str, float]:
        """Assign in a spiral pattern from pole to pole."""
        # Spiral parameter
        t = theta / math.pi + phi / (8 * math.pi)
        t = t % 1.0
        
        # Map to states
        n_states = len(sorted_states)
        state_idx = int(t * n_states) % n_states
        state = sorted_states[state_idx][0]
        
        return state, probs[state]
    
    def encode_heartbeat(self, heartbeat_result) -> LayeredEncodingResult:
        """
        Encode a heartbeat result with pattern auto-update.
        """
        # Update pattern from heartbeat
        self.pattern.update_from_heartbeat(heartbeat_result)
        
        # Store in history
        self.heartbeat_history.append(heartbeat_result)
        if len(self.heartbeat_history) > 10:
            self.heartbeat_history = self.heartbeat_history[-10:]
        
        # Encode
        return self.encode(heartbeat_result.counts, self.time)
    
    def encode_temporal(
        self,
        heartbeat_results: List,
        blend_mode: str = "layered"
    ) -> LayeredEncodingResult:
        """
        Encode multiple heartbeats showing temporal evolution.
        
        blend_mode:
        - "layered": Recent on top, older underneath
        - "averaged": Blend all together
        - "animated": Returns data for animation
        """
        if not heartbeat_results:
            return self.encode({})
        
        if blend_mode == "averaged":
            # Combine all counts
            combined = {}
            for r in heartbeat_results:
                for state, count in r.counts.items():
                    combined[state] = combined.get(state, 0) + count
            return self.encode(combined)
        
        elif blend_mode == "layered":
            # Update temporal history
            for r in heartbeat_results:
                total = sum(r.counts.values())
                probs = {s: c/total for s, c in r.counts.items()}
                self.pattern.metaphysical.temporal_states.append(probs)
            
            # Encode latest with temporal context
            latest = heartbeat_results[-1]
            coherence = latest.coherence_estimate
            self.pattern.metaphysical.coherence_value = coherence
            return self.encode(latest.counts)
        
        else:
            # Default to latest
            return self.encode_heartbeat(heartbeat_results[-1])
    
    def set_vision(self, pattern_type: str, active: bool = True):
        """Activate metaphysical vision overlay."""
        self.pattern.metaphysical.vision_active = active
        self.pattern.metaphysical.vision_pattern = pattern_type
    
    def set_resonance(self, l: int, m: int, amplitude: float = 0.3):
        """Set spherical harmonic resonance pattern."""
        self.pattern.metaphysical.resonance_l = l
        self.pattern.metaphysical.resonance_m = m
        self.pattern.metaphysical.resonance_amplitude = amplitude
    
    def add_entanglement(
        self, 
        pos1: Tuple[float, float], 
        pos2: Tuple[float, float]
    ):
        """Add entangled pair of positions."""
        self.pattern.metaphysical.entangled_pairs.append((pos1, pos2))


# Factory functions for preset encoders
def create_coherence_encoder(sphere: Sphere) -> LayeredEncoder:
    """Encoder optimized for coherence visualization."""
    return LayeredEncoder(sphere, create_coherence_pattern())


def create_temporal_encoder(sphere: Sphere) -> LayeredEncoder:
    """Encoder optimized for temporal evolution."""
    return LayeredEncoder(sphere, create_temporal_pattern())


def create_entanglement_encoder(sphere: Sphere) -> LayeredEncoder:
    """Encoder for showing entanglement patterns."""
    return LayeredEncoder(sphere, create_entanglement_pattern())


def create_vision_encoder(
    sphere: Sphere, 
    vision_type: str = "wave"
) -> LayeredEncoder:
    """Encoder with active metaphysical vision."""
    return LayeredEncoder(sphere, create_vision_pattern(vision_type))
