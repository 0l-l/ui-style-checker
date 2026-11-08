# ui-style-toolkit

I made this for 15-114 HW8 after spending several assignments repeating the same UI feedback: give the text more room, make the game easier to understand, keep the art consistent, and leave the colors and timing easy to edit.

The toolkit has two parts. `ui-style-check/` is a skill that reviews a page or game and reports what needs attention without changing files. `mcp_server/` provides `get_style_reference`, an MCP tool that reads the HTML and CSS in my earlier projects. The checker uses those projects as references when reviewing new work.

In fab-finder (HW6), I asked for a minimal, centered, black-and-white page, then had to point out that the result was too cramped to read. In Void Hop, my feedback was “I can't tell what these are” and “it's not very clear how to play.” For Tarot, I wanted to be able to change the timing and colors myself. Cozy Cat Café's HW7 README says “No emoji in the final art.”

I turned those requests into review rules. I also wanted the agent to look at my earlier work instead of guessing what “my style” meant. My repositories already contain examples, from Tarot's Cormorant Garamond and Montserrat pairing to Cat Café's warm paper and wood colors. The tool makes those choices available with source locations.

The checker identifies the project as a tool or game, calls `get_style_reference` for that kind, and reads the project's source. It checks 18 rules across color, typography, layout, game readability, art, and editability. Each rule gets one line:

```
[PASS | FIX | N/A] <category> – <rule> – <evidence>
```

The report ends with three suggested fixes in priority order. A PASS needs a file and line number or a screenshot. Rules that do not apply should be N/A. The skill reviews the implementation rather than accepting claims in comments or the README, and it must not write to the project. If the reference tool is unavailable, it says so and uses the written rules alone.

The MCP tool accepts `"tool"`, `"game"`, or `"all"` (the default). It reads the project folders listed in `mcp_server/projects.json` and scans `.html`, `.htm`, and `.css` files, excluding `.git`, `node_modules`, and `.venv`. The response lists root-level CSS variables for light and dark mode, fonts, layout values, and breakpoints, with file and line references. It also reports missing or unreadable files and notes fonts and colors shared across projects.

The server is read-only and logs to stderr so stdout stays available for MCP. The scanner uses only Python's standard library and can run without the MCP package.

## Setup

My tested setup was Windows 11, Python 3.13, and the Claude desktop app. The paths below are from my machine; change them to match your clone and reference projects.

First, create a Python environment and install the dependencies:

```
cd C:\Users\olivi\Documents\GitHub\ui-style-toolkit
python -m venv .venv
.venv\Scripts\python -m pip install -r mcp_server\requirements.txt
```

Edit `mcp_server/projects.json`. Each entry has a folder path and a kind. Use forward slashes in the JSON paths:

```
{
  "tarot": { "path": "C:/Users/olivi/Documents/GitHub/tarot", "kind": "tool" },
  "codycatcafe": { "path": "C:/Users/olivi/Documents/GitHub/codycatcafe", "kind": "game" }
}
```

Entries marked `site` are included only when requesting `all`. To check that the scanner can read your game folders, run:

```
.venv\Scripts\python mcp_server\test_scan.py game
```

The output should list the matching projects and source locations for their style values.

I used the repository's `.mcpb` package for Claude Desktop. In `extension/manifest.json`, set `server.mcp_config.command` to your virtual environment's Python executable. My configuration is:

```
"command": "C:/Users/olivi/Documents/GitHub/ui-style-toolkit/.venv/Scripts/python.exe",
"args": ["${__dirname}/server/server.py"]
```

Build the package:

```
.venv\Scripts\python extension\build_mcpb.py
```

The script checks the Python path and required server files, then writes `extension/dist/ui-style-reference.mcpb`. Open that file with Claude Desktop to install it and restart the app. In a new chat, ask “What fonts and colors have I used in my game projects?” In my tests, this produced a UI Style Reference: Get style reference call with `game` as the argument.

The package contains copies of the server files and `projects.json`. Rebuild and reinstall it after changing either.

Create a zip of the skill folder:

```
python -m zipfile -c ui-style-check.zip ui-style-check
```

In my tested version of the Claude app, I uploaded it under Settings → Capabilities → Skills, replacing the older copy when testing v2. A plain request such as “Review the visual style of this folder. It's a game.” loaded the skill without naming it.

I have not tested this toolkit in Claude Code, Codex, or other clients. For another MCP client, the server entry point is `mcp_server/server.py`, run with the virtual environment's Python executable over stdio; skill installation depends on the client.

## Test results and limits

I tested Cozy Cat Café and fab-finder using a separate working session and review session for each. Both review sessions called the reference tool, cited values from earlier projects, and left the working tree clean. [DEMONSTRATION.md](DEMONSTRATION.md) contains the prompts, report excerpts, and screenshot references.

The first version also gave PASS marks to rules that did not apply. I revised the wording and reran both reviews. The incorrect PASS marks were corrected, but one v2 report omitted an N/A row. [ITERATION.md](ITERATION.md) documents the change and the remaining problem.

There are a few other limits:

- Game references currently include Cat Café and Bughouse Chess. Shadow Dex and Void Hop sit inside `0l-l.github.io`, which is listed as `site`, so a `game` request misses them. They need separate game entries.
- Minified CSS gives less useful citations: many Bughouse Chess values point to the same few long lines.
- Without a screenshot, the checker infers layout from code. Its suspected fab-finder menu overlap still needs a browser check.
- Past style choices are useful references, but they do not prove that every project needs the same fonts or controls. I discuss the recommendations I would accept or question in the demonstration.
