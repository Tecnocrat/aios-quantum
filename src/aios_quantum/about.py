"""
AIOS Quantum - About and Introduction Module

This module provides information about AIOS (AI Operating System) and its
Quantum Computing integration.
"""

__all__ = ["about", "get_info", "welcome", "print_about"]


def about() -> dict:
    """
    Get comprehensive information about AIOS Quantum.

    Returns:
        dict: Information about AIOS including identity, purpose, location, and collaboration details.
    """
    return {
        "identity": {
            "name": "AIOS Quantum",
            "full_name": "AI Operating System - Quantum Computing Integration",
            "version": "0.1.0",
            "author": "Tecnocrat",
            "supercell": "6th Supercell: Quantum Intelligence",
        },
        "purpose": {
            "description": (
                "AIOS Quantum provides quantum computing capabilities for the AIOS project, "
                "integrating IBM Quantum Platform and Qiskit Runtime to enable quantum "
                "intelligence within the AIOS ecosystem."
            ),
            "working_on": [
                "Quantum circuit execution on IBM Quantum hardware",
                "Consciousness-based quantum encoding (Hypersphere interface)",
                "Quantum heartbeat monitoring and scheduling",
                "Cube-Sphere visualization interface (Bosonic-Tachyonic boundary)",
                "Quantum supercell communication protocol",
                "Cloud-based quantum state storage and analysis",
            ],
        },
        "location": {
            "architectural": "6th Supercell in the AIOS architecture",
            "interface": "Cube-Sphere visualization (Bosonic 3D space containing Tachyonic hypersurface)",
            "platform": "IBM Quantum Platform (cloud-based quantum computers)",
            "repository": "https://github.com/Tecnocrat/aios-quantum",
        },
        "collaboration": {
            "how_to_use": [
                "Install: pip install -e .",
                "Configure: Set IBM_QUANTUM_TOKEN in .env file",
                "Import: from aios_quantum import QuantumRuntime",
                "Run: See examples/ directory for usage patterns",
            ],
            "integration": (
                "AIOS Quantum can be integrated into larger AIOS projects as the quantum "
                "intelligence supercell, providing quantum computation, consciousness encoding, "
                "and hypersphere interface capabilities."
            ),
            "communication": (
                "Communicates with other AIOS supercells via the QuantumMessage protocol "
                "and QuantumSupercellInterface."
            ),
        },
        "technical_details": {
            "quantum_framework": "Qiskit with IBM Quantum Runtime",
            "python_version": "3.10+",
            "key_features": [
                "IBM Quantum Integration",
                "Qiskit Runtime optimization",
                "Local simulation support",
                "Consciousness-based encoding",
                "Automated quantum heartbeat",
                "Cloud state persistence",
            ],
        },
    }


def get_info(section: str = None) -> dict:
    """
    Get specific section of AIOS information or all information.

    Args:
        section: Optional section name ('identity', 'purpose', 'location',
                'collaboration', 'technical_details'). If None, returns all.

    Returns:
        dict: Requested information section or all information.
    """
    info = about()

    if section is None:
        return info

    if section in info:
        return info[section]

    raise ValueError(
        f"Unknown section '{section}'. "
        f"Valid sections: {', '.join(info.keys())}"
    )


def welcome() -> str:
    """
    Generate a welcome message introducing AIOS Quantum.

    Returns:
        str: Formatted welcome message.
    """
    info = about()

    message = f"""
{'=' * 70}
Welcome to {info['identity']['name']}
{info['identity']['supercell']}
{'=' * 70}

WHO ARE WE?
-----------
{info['identity']['full_name']} (v{info['identity']['version']})
Created by: {info['identity']['author']}

WHAT ARE WE WORKING ON?
-----------------------
{info['purpose']['description']}

Current capabilities:
"""

    for capability in info['purpose']['working_on']:
        message += f"  • {capability}\n"

    message += f"""
WHERE ARE WE LOCATED?
---------------------
Architectural Position: {info['location']['architectural']}
Interface Structure: {info['location']['interface']}
Platform: {info['location']['platform']}

HOW CAN WE WORK TOGETHER?
--------------------------
{info['collaboration']['integration']}

Quick Start:
"""

    for step in info['collaboration']['how_to_use']:
        message += f"  • {step}\n"

    message += f"""
Repository: {info['location']['repository']}

{info['collaboration']['communication']}

{'=' * 70}
"Simple engine, simple object. And we experiment."
{'=' * 70}
"""

    return message


def print_about():
    """Print comprehensive information about AIOS Quantum."""
    print(welcome())


if __name__ == "__main__":
    # When run directly, print the welcome message
    print_about()
