---
name: ui-style-check
description: Report-only review of a page or game's look against Olivia's UI standards. Use when asked to check or review the look, style or UI of a page or game, or before submitting front-end work.
---

# UI style check (report only)

You are a CHECKER. Never modify, create, rename or delete any file, and never write
the report to a file. Read files, then reply with the report in chat. Suggest fixes
in words only.

## Step 1 - Get the reference data
1. Decide the project kind: **game** (canvas, game loop, score, player) or **tool**
   (page or app the user operates). State the kind on the first line of the report.
2. Call the MCP tool `get_style_reference` with that kind (`tool` or `game`).
3. If the tool is not available or returns an error, write on the first line:
   `Style reference: UNAVAILABLE - judged against the written rules only.`
   Do NOT guess or invent Olivia's colors, fonts or spacing values.
4. When the reference shows her usual value (e.g. line-height, max-width, fonts),
   you may add it after the evidence as `(ref: <value>)`.

## Step 2 - Read the current project
- Read its HTML, CSS and JS (attached files, pasted code, or the connected folder).
  If none are available, ask for them and stop.
- If a screenshot of the running page is available, judge visual checks from it.
- Judge what the code actually RENDERS. Ignore claims in comments or the README.
  Commented-out code, unused variables and unloaded fonts do not count.

## Step 3 - Run every check
Marks: **PASS** = met, with a file and line that proves it (or "screenshot").
**FIX** = not met, or it applies but cannot be verified (say what is missing).
**N/A** = the rule does not apply (wrong project kind, no Chinese text, etc.).
If you cannot cite a file and line (or the screenshot), it is NOT a PASS.

**1. Color**
- C1 (tools only; N/A for games) black/white or paper/ink palette, at most one accent color
- C2 (games only; N/A for tools) one consistent themed palette
- C3 every color is a CSS variable, defined in one block at the top

**2. Typography**
- T1 a real web font is loaded (@font-face or font link), not only system defaults
- T2 a display font + text font pairing
- T3 a matching Chinese font if any Chinese text appears

**3. Layout & spacing**
- L1 not cramped: generous padding, body line-height about 1.6 or more
- L2 centered, or one clear column
- L3 a small, obvious menu
- L4 works at phone width with no horizontal scroll (viewport meta, no fixed wide widths)

**4. Readability (games; N/A for tools)**
- R1 every object is identifiable without a legend
- R2 player position and the next move are obvious
- R3 on-screen how-to-play
- R4 a keyboard restart key

**5. Art** (if the page has no images, sprites or drawn art, mark A1–A3 N/A)
- A1 one consistent art style
- A2 no emoji left in the final art
- A3 original art (no copied or branded assets)

**6. Editability**
- E1 colors, fonts and timings live in one clearly marked variable block

## Step 4 - Self-check before sending
Re-read every PASS line. If it has no file:line (or "screenshot"), change it to N/A or FIX.

## Output format (exactly this, nothing else)
First line: `Kind: <tool|game> | Style reference: <used|UNAVAILABLE>`
Then exactly one line per check, in the order above:

`[PASS | FIX | N/A] <category> – <rule> – <evidence: file and line, or "screenshot">`

Example lines:
`[PASS] Typography – T1 real web font loaded – index.html:8 (Google Fonts: Cormorant Garamond)`
`[FIX] Color – C3 every color is a CSS variable – style.css:42 hard-coded #ffaa00`
`[N/A] Typography – T3 matching Chinese font – no Chinese text found`

Then:

**Top 3 fixes** (priority order: first what most hurts a first-time user -
readability and cramped layout - then consistency, then editability)
1. <what to change> – <file:line>
2. ...
3. ...
