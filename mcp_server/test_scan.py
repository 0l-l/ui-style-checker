"""Run the scanner directly on the real folders (no MCP involved).

Usage:  python test_scan.py            (kind = all)
        python test_scan.py game       (or: tool)
"""
import sys

from style_scan import build_reference

sys.stdout.reconfigure(encoding="utf-8")  # safe for Chinese text in PowerShell

kind = sys.argv[1] if len(sys.argv) > 1 else "all"
print(build_reference(kind))
