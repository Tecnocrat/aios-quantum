# AINLP.provenance:
#   origin: cloud_agent (autonomous)
#   reviewed: opus (2025-12-11)
#   tests_for: src/aios_quantum/about.py
"""Tests for the about module."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum import about, get_info, print_about, welcome


class TestAbout:
    """Tests for the about functionality."""

    def test_about_returns_dict(self):
        """about() should return a dictionary."""
        info = about()
        assert isinstance(info, dict)

    def test_about_has_required_sections(self):
        """about() should contain all required information sections."""
        info = about()
        required_sections = [
            "identity",
            "purpose",
            "location",
            "collaboration",
            "technical_details",
        ]
        for section in required_sections:
            assert section in info, f"Missing section: {section}"

    def test_identity_section(self):
        """Identity section should contain basic project information."""
        info = about()
        identity = info["identity"]

        assert "name" in identity
        assert "version" in identity
        assert "author" in identity
        assert identity["name"] == "AIOS Quantum"
        assert identity["author"] == "Tecnocrat"

    def test_purpose_section(self):
        """Purpose section should describe what AIOS is working on."""
        info = about()
        purpose = info["purpose"]

        assert "description" in purpose
        assert "working_on" in purpose
        assert isinstance(purpose["working_on"], list)
        assert len(purpose["working_on"]) > 0

    def test_location_section(self):
        """Location section should describe where AIOS is located."""
        info = about()
        location = info["location"]

        assert "architectural" in location
        assert "interface" in location
        assert "platform" in location
        assert "repository" in location

    def test_collaboration_section(self):
        """Collaboration section should explain how to work with AIOS."""
        info = about()
        collaboration = info["collaboration"]

        assert "how_to_use" in collaboration
        assert "integration" in collaboration
        assert "communication" in collaboration
        assert isinstance(collaboration["how_to_use"], list)

    def test_technical_details_section(self):
        """Technical details section should provide implementation info."""
        info = about()
        technical = info["technical_details"]

        assert "quantum_framework" in technical
        assert "python_version" in technical
        assert "key_features" in technical
        assert isinstance(technical["key_features"], list)


class TestGetInfo:
    """Tests for the get_info function."""

    def test_get_info_no_section_returns_all(self):
        """get_info() with no section should return all information."""
        all_info = get_info()
        direct_info = about()
        assert all_info == direct_info

    def test_get_info_with_valid_section(self):
        """get_info() with valid section should return that section."""
        identity = get_info("identity")
        assert isinstance(identity, dict)
        assert "name" in identity
        assert identity["name"] == "AIOS Quantum"

    def test_get_info_all_sections(self):
        """get_info() should work for all valid sections."""
        sections = ["identity", "purpose", "location", "collaboration", "technical_details"]
        for section in sections:
            result = get_info(section)
            assert isinstance(result, dict), f"Section {section} should return a dict"
            assert len(result) > 0, f"Section {section} should not be empty"

    def test_get_info_invalid_section(self):
        """get_info() with invalid section should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_info("invalid_section")

        assert "Unknown section" in str(exc_info.value)
        assert "invalid_section" in str(exc_info.value)


class TestWelcome:
    """Tests for the welcome function."""

    def test_welcome_returns_string(self):
        """welcome() should return a string."""
        message = welcome()
        assert isinstance(message, str)

    def test_welcome_contains_key_information(self):
        """welcome() message should contain key information about AIOS."""
        message = welcome()

        # Check for key sections
        assert "Welcome to AIOS Quantum" in message
        assert "WHO ARE WE?" in message
        assert "WHAT ARE WE WORKING ON?" in message
        assert "WHERE ARE WE LOCATED?" in message
        assert "HOW CAN WE WORK TOGETHER?" in message

        # Check for key details
        assert "Tecnocrat" in message
        assert "6th Supercell" in message
        assert "IBM Quantum" in message

    def test_welcome_message_not_empty(self):
        """welcome() should return a substantial message."""
        message = welcome()
        assert len(message) > 500  # Should be a comprehensive message

    def test_welcome_ends_with_quote(self):
        """welcome() should end with the AIOS quote."""
        message = welcome()
        assert "Simple engine, simple object. And we experiment." in message


class TestPrintAbout:
    """Tests for the print_about function."""

    def test_print_about_runs_without_error(self, capsys):
        """print_about() should run without errors and produce output."""
        print_about()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_about_contains_welcome_content(self, capsys):
        """print_about() should print the welcome message."""
        print_about()
        captured = capsys.readouterr()

        # Should contain same content as welcome()
        assert "Welcome to AIOS Quantum" in captured.out
        assert "Tecnocrat" in captured.out
        assert "6th Supercell" in captured.out
