"""Pack the MCP server into a Claude Desktop extension (.mcpb = a zip).

Zip layout:  manifest.json
             server/server.py, server/style_scan.py, server/projects.json
The server files are copied from ../mcp_server, so that folder stays the only source.
Run:  <venv python.exe> build_mcpb.py
"""
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "mcp_server"
OUT = HERE / "dist" / "ui-style-reference.mcpb"
FILES = ["server.py", "style_scan.py", "projects.json"]

manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))  # fails loudly on a typo
python = Path(manifest["server"]["mcp_config"]["command"])
if not python.exists():
    raise SystemExit(f"python.exe in manifest.json not found: {python}")

missing = [f for f in FILES if not (SRC / f).exists()]
if missing:
    raise SystemExit(f"missing in {SRC}: {missing}")

OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(HERE / "manifest.json", "manifest.json")
    for f in FILES:
        z.write(SRC / f, f"server/{f}")

print(f"Built: {OUT}")
for name in zipfile.ZipFile(OUT).namelist():
    print(f"  {name}")
