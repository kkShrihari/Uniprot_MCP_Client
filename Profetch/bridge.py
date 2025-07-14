"""
Bridge module for uniPROscope MCP Client.
"""

import requests
import asyncio
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
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = requests.Session()

    async def get_gene_info(self, gene_symbol: str) -> Dict[str, Any]:
        """Fetch detailed gene/protein information from UniProt API."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_gene_info_sync, gene_symbol)

    def _get_gene_info_sync(self, gene_symbol: str) -> Dict[str, Any]:
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

            # Extract synonyms
            synonyms = []
            for gene in entry.get("genes", []):
                for syn in gene.get("synonyms", []):
                    val = syn.get("value")
                    if val:
                        synonyms.append(val)
            gene_synonyms = list(dict.fromkeys(synonyms))[:10] or ["No data available"]

            # Extract GO terms
            go_terms = []
            for ref in entry.get("uniProtKBCrossReferences", []):
                if ref.get("database") == "GO":
                    go_id = ref.get("id", "")
                    for prop in ref.get("properties", []):
                        if prop.get("key") == "GoTerm":
                            go_terms.append(f"{go_id}: {prop['value']}")
            go_terms = list(dict.fromkeys(go_terms))[:10] or ["No data available"]

            # Extract subcellular locations
            locations = []
            for comment in entry.get("comments", []):
                if comment.get("commentType") == "SUBCELLULAR LOCATION":
                    for loc in comment.get("subcellularLocations", []):
                        val = loc.get("location", {}).get("value")
                        if val:
                            locations.append(val)
            subcellular_location = list(dict.fromkeys(locations))[:10] or ["No data available"]

            # Extract interactions
            interactions = []
            for comment in entry.get("comments", []):
                if comment.get("commentType") == "INTERACTION":
                    for interactor in comment.get("interactions", []):
                        interactor_id = interactor.get("interactantTwo", {}).get("uniProtKBAccession")
                        if interactor_id:
                            interactions.append(interactor_id)
            interactions = list(dict.fromkeys(interactions))[:10] or ["No data available"]

            # Extract function description
            function_text = "No data available"
            for comment in entry.get("comments", []):
                if comment.get("commentType") == "FUNCTION":
                    function_text = comment.get("texts", [{}])[0].get("value", function_text)
                    break

            return {
                "gene": gene_symbol.upper(),
                "uniprot_id": entry.get("primaryAccession", "No data available"),
                "entry_name": entry.get("uniProtkbId", "No data available"),
                "protein_name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "No data available"),
                "gene_synonyms": gene_synonyms,
                "organism": entry.get("organism", {}).get("scientificName", "No data available"),
                "sequence_length": entry.get("sequence", {}).get("length", "No data available"),
                "mass": entry.get("sequence", {}).get("mass", "No data available"),
                "chromosome": entry.get("comments", [{}])[0].get("location", {}).get("value", "No data available"),
                "function": function_text,
                "go_terms": go_terms,
                "subcellular_location": subcellular_location,
                "interactions": interactions,
                #"entry": entry  # Optional: raw UniProt JSON for debug/testing
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_protein_expression(self, gene_symbol: str) -> str:
        info = await self.get_gene_info(gene_symbol)
        return info.get("function", "No data available")

    async def get_subcellular_location(self, gene_symbol: str) -> List[str]:
        info = await self.get_gene_info(gene_symbol)
        return info.get("subcellular_location", ["No data available"])

    async def fetch_uniprot_entry(self, gene_symbol: str) -> Dict[str, Any]:
        """For testing raw UniProt JSON structure."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_gene_info_sync, gene_symbol)
