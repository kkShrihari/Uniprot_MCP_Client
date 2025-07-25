# Uniport_MCP_Client

`Uniport_MCP_Client` is a Python package that integrates UniProt gene and protein data with the Model Context Protocol (MCP), enabling querying and exploration of gene function, subcellular localization, and protein expression through both CLI and MCP interfaces. An MCP (Model Context Protocol) extension that fetches human gene and protein data from **UniProt** using Claude-compatible tools.

## 📦 Features

This MCP extension provides 3 tools callable by Claude:

- 🔍 **`get_gene_info`**  
  Fetch detailed UniProt information for a human gene symbol (e.g., TP53). Returns UniProt ID, protein name, synonyms, GO terms, subcellular locations, function, and more.

- 🧬 **`get_protein_expression`**  
  Returns the biological function summary of a protein corresponding to the given gene.

- 🧫 **`get_subcellular_location`**  
  Lists known subcellular locations for the protein product of the gene.

## 🧠 Tech Stack

- MCP Extension (Claude-compatible)
- Python 3.10+
- UniProt REST API
- Libraries: `requests`, `httpx`, `pydantic`, `starlette`, `uvicorn`, `typer`, `websockets`, etc.

## 🗂 Project Structure

```
Uniport_MCP_Client/
├── Profetch/
│   ├── __init__.py
│   ├── bridge.py
│   ├── mcp_server.py
│   └── mcp/                  # MCP support code (server, client, cli, etc.)
├── manifest.json             # Defines MCP tools and server entrypoint
├── pyproject.toml            # Package metadata and dependencies
```

## 🔧 Installing Dependencies (Optional for Development)

If you want to test or develop locally:

```bash
# From the root of your project (same folder as pyproject.toml)
pip install -e .
```

To install development tools (optional):

```bash
pip install -e .[dev]
```

## 🤖 Using the Extension with Claude (Production Use)

1. **Package your extension** folder as a `.dxt` file (zip format):
   - Make sure the `manifest.json` is at the root.
   - Include `pyproject.toml`, the `Profetch` folder (with `bridge.py`, `mcp_server.py`, etc.).

2. **Upload the `.dxt` file to Claude** via the "Add Extension" option in Claude Desktop or Web.

3. Claude will **automatically start the server** using your `manifest.json`:

   ```json
   "entry_point": "Profetch/mcp_server.py",
   "args": ["--serve"]
   ```

4. Now you can call your tools from Claude:

   - `get_gene_info`
   - `get_protein_expression`
   - `get_subcellular_location`

   Example call:
   ```json
   {
     "tool": "get_gene_info",
     "parameters": {
       "gene_symbol": "TP53"
     }
   }
   ```

---

## 📜 License

MIT © Shrihari Kamalann Kumaraguruparan
