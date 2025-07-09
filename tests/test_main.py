"""
Tests for uniPROscope MCP Client main module.
"""

import pytest
from Profetch.bridge import Bridge, Config


class TestConfig:
    """Test the Config class."""

    def test_default_config(self):
        config = Config()
        assert config.base_url == "https://rest.uniprot.org"
        assert config.timeout == 30.0
        assert config.request_delay == 1.0

    def test_custom_config(self):
        config = Config(
            base_url="https://custom.api.com",
            timeout=60.0,
            request_delay=2.0,
            api_key="test_key"
        )
        assert config.base_url == "https://custom.api.com"
        assert config.api_key == "test_key"
        assert config.timeout == 60.0
        assert config.request_delay == 2.0


class TestBridge:
    """Test the Bridge class."""

    def test_bridge_initialization(self):
        bridge = Bridge()
        assert bridge.config.base_url == "https://rest.uniprot.org"

    def test_bridge_initialization_with_config(self):
        config = Config(api_key="test_key")
        bridge = Bridge(config)
        assert bridge.config.api_key == "test_key"

    def test_get_gene_info_valid(self):
        bridge = Bridge()
        result = bridge.get_gene_info("TP53")
        assert isinstance(result, dict)
        assert result.get("gene", "") == "TP53"
        assert "uniprot_id" in result
        assert "function" in result

    def test_get_gene_info_invalid(self):
        bridge = Bridge()
        result = bridge.get_gene_info("FAKEGENE1234XYZ")
        assert isinstance(result, dict)
        assert "error" in result

    def test_get_protein_expression_valid(self):
        bridge = Bridge()
        result = bridge.get_protein_expression("TP53")
        assert isinstance(result, str)
        assert "No function annotation available." not in result

    def test_get_subcellular_location_valid(self):
        bridge = Bridge()
        result = bridge.get_subcellular_location("TP53")
        assert isinstance(result, list)
        assert all(isinstance(loc, str) for loc in result)
