"""
Surface Encoder

Maps quantum measurement results onto the sphere surface.
This is the bridge between quantum data and visual representation.

The encoding strategies translate abstract quantum patterns
into spatial arrangements on the tachyonic surface.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .geometry import Sphere, Color, Point3D, SurfacePoint


@dataclass
class EncodingResult:
    """Result of encoding quantum data onto sphere."""
    points_encoded: int
    total_probability: float
    dominant_state: str
    coherence: float
    entropy: float


class SurfaceEncoder:
    """
    Encodes quantum measurement results onto a sphere surface.
    
    Multiple encoding strategies available:
    - Sequential: States mapped in order around sphere
    - Probability: Higher probability states get more points
    - Harmonic: States mapped to spherical harmonics
    - Coherence: Pattern based on measurement coherence
    """
    
    def __init__(self, sphere: Sphere):
        self.sphere = sphere
    
    def encode_counts(
        self, 
        counts: Dict[str, int],
        strategy: str = "probability"
    ) -> EncodingResult:
        """
        Encode measurement counts onto sphere surface.
        
        Args:
            counts: Dictionary of {state: count}
            strategy: Encoding strategy to use
            
        Returns:
            EncodingResult with encoding statistics
        """
        if strategy == "sequential":
            return self._encode_sequential(counts)
        elif strategy == "probability":
            return self._encode_probability(counts)
        elif strategy == "harmonic":
            return self._encode_harmonic(counts)
        elif strategy == "spiral":
            return self._encode_spiral(counts)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _encode_sequential(self, counts: Dict[str, int]) -> EncodingResult:
        """
        Sequential encoding: each state gets equal space.
        States are mapped around the sphere in binary order.
        """
        self.sphere.clear()
        
        if not counts:
            return EncodingResult(0, 0, "", 0, 0)
        
        total = sum(counts.values())
        sorted_states = sorted(counts.keys())
        n_states = len(sorted_states)
        points_per_state = max(1, self.sphere.point_count // n_states)
        
        idx = 0
        for i, state in enumerate(sorted_states):
            prob = counts[state] / total
            for _ in range(points_per_state):
                if idx < self.sphere.point_count:
                    self.sphere.encode_quantum_state(state, prob, idx)
                    idx += 1
        
        # Calculate metrics
        probs = [c/total for c in counts.values()]
        coherence = max(probs)
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        dominant = max(counts, key=counts.get)
        
        return EncodingResult(
            points_encoded=idx,
            total_probability=1.0,
            dominant_state=dominant,
            coherence=coherence,
            entropy=entropy
        )
    
    def _encode_probability(self, counts: Dict[str, int]) -> EncodingResult:
        """
        Probability encoding: states get points proportional to probability.
        Higher probability = more surface coverage.
        """
        self.sphere.clear()
        
        if not counts:
            return EncodingResult(0, 0, "", 0, 0)
        
        total = sum(counts.values())
        sorted_states = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Assign points proportionally
        idx = 0
        for state, count in sorted_states:
            prob = count / total
            n_points = max(1, int(prob * self.sphere.point_count))
            
            for _ in range(n_points):
                if idx < self.sphere.point_count:
                    self.sphere.encode_quantum_state(state, prob, idx)
                    idx += 1
        
        # Fill remaining with dominant state
        if idx < self.sphere.point_count and sorted_states:
            dominant_state = sorted_states[0][0]
            dominant_prob = sorted_states[0][1] / total
            while idx < self.sphere.point_count:
                self.sphere.encode_quantum_state(dominant_state, dominant_prob, idx)
                idx += 1
        
        # Calculate metrics
        probs = [c/total for c in counts.values()]
        coherence = max(probs)
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        dominant = sorted_states[0][0] if sorted_states else ""
        
        return EncodingResult(
            points_encoded=idx,
            total_probability=1.0,
            dominant_state=dominant,
            coherence=coherence,
            entropy=entropy
        )
    
    def _encode_harmonic(self, counts: Dict[str, int]) -> EncodingResult:
        """
        Harmonic encoding: map states to spherical harmonic-like patterns.
        State bits determine the angular frequency of the pattern.
        """
        self.sphere.clear()
        
        if not counts:
            return EncodingResult(0, 0, "", 0, 0)
        
        total = sum(counts.values())
        
        # For each surface point, calculate contribution from all states
        for idx, sp in enumerate(self.sphere.surface_points):
            # Get spherical coordinates
            rel_pos = sp.position - self.sphere.center
            _, theta, phi = rel_pos.to_spherical()
            
            # Accumulate color from all states
            r, g, b = 0.0, 0.0, 0.0
            total_weight = 0.0
            
            for state, count in counts.items():
                prob = count / total
                
                # State determines harmonic pattern
                try:
                    state_int = int(state, 2)
                    n_bits = len(state)
                except ValueError:
                    state_int = 0
                    n_bits = 1
                
                # Harmonic weight based on state and position
                l = state_int % (n_bits + 1)  # "degree"
                m = (state_int // (n_bits + 1)) % (2 * l + 1) - l  # "order"
                
                # Simplified spherical harmonic-like pattern
                harmonic = math.cos(l * theta) * math.cos(m * phi)
                weight = (1 + harmonic) / 2 * prob  # Normalize to [0, 1]
                
                # Color from state
                color = Color.from_quantum_state(state, prob)
                r += color.r * weight
                g += color.g * weight
                b += color.b * weight
                total_weight += weight
            
            # Normalize and apply
            if total_weight > 0:
                sp.color = Color(
                    min(1, r/total_weight),
                    min(1, g/total_weight),
                    min(1, b/total_weight)
                )
                sp.intensity = total_weight
        
        # Metrics
        probs = [c/total for c in counts.values()]
        coherence = max(probs)
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        dominant = max(counts, key=counts.get)
        
        return EncodingResult(
            points_encoded=self.sphere.point_count,
            total_probability=1.0,
            dominant_state=dominant,
            coherence=coherence,
            entropy=entropy
        )
    
    def _encode_spiral(self, counts: Dict[str, int]) -> EncodingResult:
        """
        Spiral encoding: states flow in a spiral from pole to pole.
        Creates a temporal narrative on the surface.
        """
        self.sphere.clear()
        
        if not counts:
            return EncodingResult(0, 0, "", 0, 0)
        
        total = sum(counts.values())
        sorted_states = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create spiral path through surface points
        n_points = self.sphere.point_count
        
        idx = 0
        for state, count in sorted_states:
            prob = count / total
            n_assigned = max(1, int(prob * n_points))
            
            for _ in range(n_assigned):
                if idx >= n_points:
                    break
                    
                # Spiral position
                t = idx / n_points
                theta = math.pi * t  # Pole to pole
                phi = 8 * math.pi * t  # Multiple rotations
                
                # Find closest surface point to this position
                target = Point3D.from_spherical(self.sphere.radius, theta, phi)
                target = target + self.sphere.center
                
                # Use direct index for simplicity (spiral already in generation)
                self.sphere.encode_quantum_state(state, prob, idx)
                idx += 1
        
        # Metrics
        probs = [c/total for c in counts.values()]
        coherence = max(probs)
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        dominant = sorted_states[0][0] if sorted_states else ""
        
        return EncodingResult(
            points_encoded=idx,
            total_probability=1.0,
            dominant_state=dominant,
            coherence=coherence,
            entropy=entropy
        )
    
    def encode_heartbeat_result(self, result) -> EncodingResult:
        """
        Encode a HeartbeatResult from the heartbeat scheduler.
        
        Uses probability encoding by default, as it best shows
        the distribution of quantum measurements.
        """
        return self.encode_counts(result.counts, strategy="probability")
    
    def encode_multiple_heartbeats(
        self, 
        results: List,
        blend: str = "temporal"
    ) -> EncodingResult:
        """
        Encode multiple heartbeat results, showing evolution over time.
        
        Args:
            results: List of HeartbeatResult objects
            blend: How to combine results ("temporal", "average", "latest")
        """
        if not results:
            self.sphere.clear()
            return EncodingResult(0, 0, "", 0, 0)
        
        if blend == "latest":
            return self.encode_heartbeat_result(results[-1])
        
        elif blend == "average":
            # Combine all counts
            combined = {}
            for r in results:
                for state, count in r.counts.items():
                    combined[state] = combined.get(state, 0) + count
            return self.encode_counts(combined, strategy="probability")
        
        elif blend == "temporal":
            # Most recent results get more surface area
            self.sphere.clear()
            n = len(results)
            points_per_result = self.sphere.point_count // n
            
            idx = 0
            for i, r in enumerate(results):
                weight = (i + 1) / n  # Later results weighted higher
                total = sum(r.counts.values())
                
                for state, count in r.counts.items():
                    prob = count / total
                    n_points = int(prob * points_per_result * weight)
                    
                    for _ in range(n_points):
                        if idx < self.sphere.point_count:
                            self.sphere.encode_quantum_state(state, prob, idx)
                            idx += 1
            
            # Use latest result for metrics
            latest = results[-1]
            total = sum(latest.counts.values())
            probs = [c/total for c in latest.counts.values()]
            
            return EncodingResult(
                points_encoded=idx,
                total_probability=1.0,
                dominant_state=max(latest.counts, key=latest.counts.get),
                coherence=max(probs),
                entropy=-sum(p * math.log2(p) for p in probs if p > 0)
            )
        
        else:
            raise ValueError(f"Unknown blend mode: {blend}")
