"""
MCP Server implementation for uniPROscope MCP Client.
"""

import json
import sys
from typing import Any, Dict, Optional

from .bridge import Bridge


class MCPServer:
    """MCP Server for uniPROscope MCP Client."""

    def __init__(self):
        self.bridge = Bridge()
        self.request_id = 0

    def send_response(self, result: Any, error: Optional[str] = None):
        """Send a JSON-RPC response."""
        response = {
            "jsonrpc": "2.0",
            "id": self.request_id,
        }

        if error:
            response["error"] = {"code": -1, "message": error}
        else:
            response["result"] = result

        print(json.dumps(response))
        sys.stdout.flush()

    def handle_request(self, request: Dict[str, Any]):
        """Handle a JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        self.request_id = request.get("id", 0)

        try:
            if method == "initialize":
                self.handle_initialize(params)
            elif method == "tools/list":
                self.handle_list_tools()
            elif method == "tools/call":
                self.handle_call_tool(params)
            else:
                self.send_response(None, f"Unknown method: {method}")
        except Exception as e:
            self.send_response(None, str(e))

    def handle_initialize(self, params: Dict[str, Any]):
        """Handle initialize request."""
        response = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "uniPROscope MCP Client",
                "version": "0.1.0"
            }
        }
        self.send_response(response)

    def handle_list_tools(self):
        """Return the list of supported tools."""
        tools = [
            {
                "name": "get_gene_info",
                "description": "Fetch full UniProt gene information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "gene_symbol": {
                            "type": "string",
                            "description": "Gene symbol (e.g., TP53)"
                        }
                    },
                    "required": ["gene_symbol"]
                }
            },
            {
                "name": "get_protein_expression",
                "description": "Fetch protein function summary",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "gene_symbol": {
                            "type": "string",
                            "description": "Gene symbol (e.g., BRCA1)"
                        }
                    },
                    "required": ["gene_symbol"]
                }
            },
            {
                "name": "get_subcellular_location",
                "description": "Fetch subcellular location info",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "gene_symbol": {
                            "type": "string",
                            "description": "Gene symbol (e.g., EGFR)"
                        }
                    },
                    "required": ["gene_symbol"]
                }
            }
        ]

        self.send_response({"tools": tools})

    def handle_call_tool(self, params: Dict[str, Any]):
        """Call the specified tool."""
        print("DEBUG: Entered handle_call_tool", file=sys.stderr)
        name = params.get("name")
        arguments = params.get("arguments", {})
        print(f"DEBUG: Tool name = {name}", file=sys.stderr)
        print(f"DEBUG: Arguments = {arguments}", file=sys.stderr)

        try:
            gene_symbol = arguments.get("gene_symbol")
            if not gene_symbol:
                raise ValueError("gene_symbol is required")

            if name == "get_gene_info":
                print(f"DEBUG: Calling get_gene_info with {gene_symbol}", file=sys.stderr)
                result = self.bridge.get_gene_info(gene_symbol)
                text = json.dumps(result, indent=2)
                self.send_response({"content": [{"type": "text", "text": text}]})

            elif name == "get_protein_expression":
                print(f"DEBUG: Calling get_protein_expression with {gene_symbol}", file=sys.stderr)
                result = self.bridge.get_protein_expression(gene_symbol)
                self.send_response({"content": [{"type": "text", "text": result}]})

            elif name == "get_subcellular_location":
                print(f"DEBUG: Calling get_subcellular_location with {gene_symbol}", file=sys.stderr)
                result = self.bridge.get_subcellular_location(gene_symbol)
                formatted = "\n".join(result) if result else "No location data found."
                self.send_response({"content": [{"type": "text", "text": formatted}]})

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}", file=sys.stderr)
            self.send_response(None, str(e))

    def run(self):
        """Main event loop."""
        print("uniPROscope MCP server ready...", file=sys.stderr)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Bad JSON from host: {e}", file=sys.stderr)
                continue

            self.handle_request(request)


# ✅ Add this to make the server run on command-line execution
if __name__ == "__main__":
    server = MCPServer()
    server.run()
