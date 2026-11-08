"""MCP server "ui-style-reference" (stdio). Exactly one tool: get_style_reference.

stdout is reserved for the MCP protocol. Never print(); use `log` (stderr).
"""
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("ui-style-reference")

from mcp.server.fastmcp import FastMCP  # noqa: E402  (logging must be set up first)

from style_scan import build_reference  # noqa: E402

mcp = FastMCP("ui-style-reference")


@mcp.tool()
def get_style_reference(kind: str = "all") -> str:
    """Return Olivia's REAL past visual style, read from the HTML/CSS of her own projects.

    Call this BEFORE reviewing, checking or designing any page, app UI or game for
    Olivia, so the work is compared with (or matches) the colors, fonts and spacing
    she actually used, instead of guessing her taste.

    Args:
        kind: "tool" (web tools such as tarot, fab-finder), "game" (browser games),
              or "all" (default: every project). Use the kind of the project being
              reviewed or built.

    Returns plain text, one section per project:
      - :root CSS custom properties, split into light and dark-mode values
      - font-family values and Google Fonts families
      - layout hints: max-width, gap, padding, line-height, @media breakpoints
      - [file:line] after every value, plus any missing folders or unreadable files
    and a final "common patterns" section listing fonts and colors used in more
    than one project. Read-only: it never changes any file.
    """
    log.info("get_style_reference(kind=%r)", kind)
    try:
        return build_reference(kind)
    except Exception as e:  # report instead of crashing the server
        log.exception("style scan failed")
        return f"ERROR: style scan failed: {e!r}"


if __name__ == "__main__":
    log.info("ui-style-reference MCP server starting (stdio). Waiting for a client; Ctrl+C to stop.")
    mcp.run(transport="stdio")
