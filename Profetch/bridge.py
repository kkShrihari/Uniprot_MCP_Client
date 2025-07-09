"""
Bridge module for uniPROscope MCP Client.
"""

import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for uniPROscope MCP Client."""
    base_url: str = "https://rest.uniprot.org"
    timeout: float = 30.0
    request_delay: float = 1.0
    api_key: Optional[str] = None


class Bridge:
    """
    Main bridge class for uniPROscope MCP Client.

    This class provides the main interface for interacting with the UniProt API.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = requests.Session()

    def get_gene_info(self, gene_symbol: str) -> Dict[str, Any]:
        """
        Fetch detailed gene/protein information from UniProt API.

        Args:
            gene_symbol: Gene symbol (e.g., TP53, BRCA1).

        Returns:
            Dictionary containing gene/protein information.
        """
        url = f"{self.config.base_url}/uniprotkb/search"
        params = {
            "query": f"gene:{gene_symbol} AND organism_id:9606",
            "format": "json"
        }

        try:
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            results = response.json()

            if not results.get("results"):
                return {"error": f"No data found for gene symbol '{gene_symbol}'"}

            entry = results["results"][0]
            return {
                "gene": gene_symbol.upper(),
                "uniprot_id": entry.get("primaryAccession"),
                "entry_name": entry.get("uniProtkbId"),
                "protein_name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value"),
                "gene_synonyms": self._extract_gene_synonyms(entry),
                "organism": entry.get("organism", {}).get("scientificName"),
                "sequence_length": entry.get("sequence", {}).get("length"),
                "mass": entry.get("sequence", {}).get("mass"),
                "chromosome": entry.get("comments", [{}])[0].get("location", {}).get("value", "N/A"),
                "function": self._extract_function(entry),
                "go_terms": self._extract_go_terms(entry),
                "subcellular_location": self._extract_subcellular_location(entry),
                "interactions": self._extract_interactions(entry)
            }

        except Exception as e:
            return {"error": str(e)}

    def get_protein_expression(self, gene_symbol: str) -> str:
        """
        Return protein function (expression summary) for the gene.
        """
        info = self.get_gene_info(gene_symbol)
        return info.get("function", "No function info")

    def get_subcellular_location(self, gene_symbol: str) -> List[str]:
        """
        Return subcellular locations for the gene.
        """
        info = self.get_gene_info(gene_symbol)
        return info.get("subcellular_location", [])

    def _extract_function(self, entry: Dict[str, Any]) -> str:
        for comment in entry.get("comments", []):
            if comment.get("commentType") == "FUNCTION":
                return comment.get("texts", [{}])[0].get("value", "No function annotation available.")
        return "No function annotation available."

    def _extract_go_terms(self, entry: Dict[str, Any]) -> List[str]:
        go_terms = []
        for ref in entry.get("uniProtKBCrossReferences", []):
            if ref.get("database") == "GO":
                go_id = ref.get("id", "")
                for prop in ref.get("properties", []):
                    if prop["key"] == "GoTerm":
                        go_terms.append(f"{go_id}: {prop['value']}")
        return go_terms

    def _extract_gene_synonyms(self, entry: Dict[str, Any]) -> List[str]:
        synonyms = []
        for gene in entry.get("genes", []):
            for syn in gene.get("synonyms", []):
                val = syn.get("value")
                if val:
                    synonyms.append(val)
        return synonyms

    def _extract_subcellular_location(self, entry: Dict[str, Any]) -> List[str]:
        locations = []
        for comment in entry.get("comments", []):
            if comment.get("commentType") == "SUBCELLULAR LOCATION":
                for loc in comment.get("subcellularLocations", []):
                    val = loc.get("location", {}).get("value")
                    if val:
                        locations.append(val)
        return locations

    def _extract_interactions(self, entry: Dict[str, Any]) -> List[str]:
        interactions = []
        for comment in entry.get("comments", []):
            if comment.get("commentType") == "INTERACTION":
                for interactor in comment.get("interactions", []):
                    interactor_id = interactor.get("interactantTwo", {}).get("uniProtKBAccession")
                    if interactor_id:
                        interactions.append(interactor_id)
        return interactions
