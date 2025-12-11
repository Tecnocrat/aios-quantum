#!/usr/bin/env python3
"""
AIOS Quantum - About AIOS Example

This example demonstrates how to get information about AIOS Quantum
and display the welcome message.
"""

import json
import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum import about, get_info, print_about, welcome


def main():
    """Demonstrate the about functionality."""

    # Option 1: Print the full welcome message
    print("\n" + "=" * 70)
    print("OPTION 1: Full Welcome Message")
    print("=" * 70)
    print_about()

    # Option 2: Get structured information
    print("\n" + "=" * 70)
    print("OPTION 2: Structured Information (JSON)")
    print("=" * 70)
    info = about()
    print(json.dumps(info, indent=2))

    # Option 3: Get specific sections
    print("\n" + "=" * 70)
    print("OPTION 3: Get Specific Sections")
    print("=" * 70)

    print("\n--- IDENTITY ---")
    identity = get_info("identity")
    for key, value in identity.items():
        print(f"  {key}: {value}")

    print("\n--- PURPOSE ---")
    purpose = get_info("purpose")
    print(f"  Description: {purpose['description']}")
    print("  Working on:")
    for item in purpose['working_on']:
        print(f"    • {item}")

    print("\n--- LOCATION ---")
    location = get_info("location")
    for key, value in location.items():
        print(f"  {key}: {value}")

    print("\n--- COLLABORATION ---")
    collaboration = get_info("collaboration")
    print(f"  Integration: {collaboration['integration']}")
    print("  How to use:")
    for step in collaboration['how_to_use']:
        print(f"    • {step}")

    print("\n--- TECHNICAL DETAILS ---")
    technical = get_info("technical_details")
    print(f"  Framework: {technical['quantum_framework']}")
    print(f"  Python: {technical['python_version']}")
    print("  Key features:")
    for feature in technical['key_features']:
        print(f"    • {feature}")

    # Option 4: Get the welcome string (for programmatic use)
    print("\n" + "=" * 70)
    print("OPTION 4: Welcome String (for programmatic use)")
    print("=" * 70)
    welcome_text = welcome()
    print(f"Welcome message is {len(welcome_text)} characters long")
    print("(Already displayed in Option 1)")


if __name__ == "__main__":
    main()
