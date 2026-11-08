# Demonstration

I tested the toolkit on Cozy Cat Café and fab-finder. For each project, one session made a small visual change after calling the reference tool. A fresh session then reviewed the result using only a plain request, without the skill name or checklist in the prompt.

I committed the first session's changes before starting the review. That made a clean `git status` a useful check that the reviewer had left the files alone. Screenshots of the calls, reports, and repository status are in `screenshots/`.

These are the recorded Claude Desktop tests, not new runs. The original notes identify both sessions as using Opus5.5. Claude drafted the original account from the screenshots and conversation; Codex later revised the writing and drafted the evaluation sections from that record. I then provided my evaluations of both projects in Chinese, and Codex translated them into English. The evaluations below explain how I would prioritize the reported issues; they do not add browser verification.

## Cozy Cat Café

Cozy Cat Café (my HW7 game) still used emoji placeholders. The HW7 README says "No emoji in the final art." I asked Session A to replace three of them with pixel art.

I gave the session this prompt:

> In C:\Users\olivi\Documents\GitHub\codycatcafe, replace the emoji placeholders for the door, bowl and seats with pixel-art drawn in CSS/SVG. Before designing, call get_style_reference with kind "game". Make only this change, then list the files you changed.

The session called UI Style Reference: Get style reference first, requesting `game` (`run1-A-steps.png`, `run1-A-toolcall.png`). Here is part of the response:

```
Style reference, kind=game: 2 project(s): codycatcafe, bughouse-chess
=== codycatcafe (game) ===
  :root custom properties (light):
    --bg: #fbf3e4  [style.css:3]
    --ink: #4a3426  [style.css:6]
    --accent: #c8693a  [style.css:7]
    --panel: #fffaf2  [style.css:8]
  font-family values:
    "Trebuchet MS", system-ui, sans-serif  [style.css:17]
  Google Fonts families: none
=== bughouse-chess (game) ===
  Google Fonts families:
    DM Sans  [frontend/assets/style.css:1]
    Space Grotesk  [frontend/assets/style.css:1]
  ...
```

The result is in `run1-A-result.png`. It drew the door, bowl and seats as pixel-art SVG in a new `sprites.js`, using `--ink`, `--accent`, and `--panel` from the reference response, plus a wood brown. It changed `sprites.js` (new), `index.html`, `style.css` and `ui.js`. It also pointed out that the cats, customers and icons were still emoji.

I gave the session this prompt:

> Review the visual style of C:\Users\olivi\Documents\GitHub\codycatcafe. It's a game.

In the fresh review session, the agent loaded the skill, called the reference tool with `game`, and read the source files with line numbers (`run1-B-steps.png`, `run1-B-toolcall.png`).

The two calls also showed that the tool was reading the updated files. In Session A's call, Cat Café had 6 color variables and the font was at `style.css:17`. In Session B's call, it also listed `--wood: #b98a5e [style.css:9]` and `--wood-dark: #8a5f3c [style.css:10]`, and the font had moved to `style.css:19`. These are Session A's edits, so the tool reads the files as they are now.

The review included the following findings (`run1-B-report.png`):

```
Kind: game | Style reference: used
[PASS] Color – C1 black/white or paper/ink palette – N/A for games (see C2)
[PASS] Color – C2 one consistent themed palette – style.css:2-11 (warm café set ...)
[FIX] Color – C3 every color is a CSS variable – style.css:62 and :157 hard-code #b98a5e (same as --wood), :158 #ffe1d2 ...
[FIX] Typography – T1 real web font loaded – style.css:19 uses only "Trebuchet MS", system-ui; index.html:7 loads no font link (ref: DM Sans / Space Grotesk via Google Fonts, bughouse-chess style.css:1)
[FIX] Layout & spacing – L4 phone width – ui.js:37 sets #shop to a fixed 640px ... (ref: (max-width:620px), bughouse-chess style.css:6)
[FIX] Readability – R3 on-screen how-to-play – index.html:10-31 has no instructions
[FIX] Readability – R4 keyboard restart key – no keydown listener ...
[FIX] Art – A1 one consistent art style – pixel-art SVG props (sprites.js:16-63) are mixed with emoji cats and customers (ui.js:78, ui.js:125)
[FIX] Art – A2 no emoji in final art – index.html:14, :15, :17, :28; ui.js:75, :76, :78, ...
[PASS] Art – A3 original art – sprites.js:16-63 (hand-made pixel grids ...)
...
Top 3 fixes
1. Add a one-line how-to-play under the header ... – index.html:18, ui.js:49, ui.js:127
2. Make the shop fit a phone ... – ui.js:37, style.css:15-22, style.css:78/:101
3. Use one art style: draw the cats, customers and icons as pixel sprites ... – ui.js:78/:125, ...
```

After the review, git still reported `nothing to commit, working tree clean` (`run1-B-gitstatus.png`).

I agree that the art should be more consistent. The door and seats are pixel art now, while the cats and customers are still emoji, and they do not look like they belong together.

I do not think this game necessarily needs a restart key. It is an ongoing cafe management game without a clear lose-and-start-over cycle. Changing the font is not urgent either: the current text is readable, so I would put instructions and phone support ahead of a new font.

## fab-finder

fab-finder (my HW6 app) has a minimal black-and-white page. I asked Session A to make the advice card easier to read on a phone, the same "too cramped" problem I complained about in HW6.

`run2-gitstatus-before.png`: the repo was clean before starting.

I gave the session this prompt:

> In C:\Users\olivi\Documents\GitHub\fab-finder, make the advice card on static/index.html easier to read on a phone: adjust spacing and font sizes for screens under 600px wide. Before designing, call get_style_reference with kind "tool". Make only this change, then list the files you changed.

It requested `tool`, which returned references from Tarot and fab-finder (`run2-A-toolcall-1.png`, `run2-A-toolcall-2.png`):

```
=== tarot (tool) ===
    --font-display: "Cormorant Garamond", "Noto Serif TC", Georgia, serif  [public/index.html:37]
    --font-label: "Montserrat", Arial, sans-serif  [public/index.html:38]
  line-height:
    1.6  [public/index.html:60]
  @media breakpoints:
    (max-width: 480px)  [public/index.html:367]
=== fab-finder (tool) ===
    --paper: #ffffff (2x)  [index.html:12, static/index.html:12]
    --ink: #000000 (2x)  [index.html:13, static/index.html:13]
    --serif: "Newsreader", "Noto Serif SC", Georgia, serif  [static/index.html:16]
```

It added styles for screens under 600px (line height 1.7 → 1.8, more space between paragraphs, slightly larger headings and citation numbers, long links wrap), and put the values in a marked "EDIT ME" block in `:root`. One file changed: `static/index.html` (`1 file changed, 31 insertions(+)`; `run2-A-result.png`, `run2-A-commit.png`).

I gave the session this prompt:

> Review the visual style of C:\Users\olivi\Documents\GitHub\fab-finder. It's a tool.

The reviewer called the reference tool with `tool` (`run2-B-toolcall-1.png`, `run2-B-toolcall-2.png`). The response already included Session A's new variables (`--card-phone-text: 1rem [static/index.html:20]` … `--card-phone-gap: 0.85rem [static/index.html:23]`).

The review included the following findings (`run2-B-report.png`):

```
Kind: tool | Style reference: used
[PASS] Color – C1 black/white palette, at most one accent – static/index.html:12-15 (--paper #ffffff, --ink #000000, two greys, no accent ...)
[N/A] Color – C2 one themed game palette – tool, not a game
[FIX] Color – C3 every color is a CSS variable – static/index.html:113 placeholder color #b4b4b4 is hard-coded
[FIX] Typography – T2 display + text font pairing – static/index.html:16 only one family (--serif = Newsreader) ... (ref: tarot pairs Cormorant Garamond + Montserrat)
[PASS] Layout – L1 not cramped – static/index.html:36 body line-height 1.6 ... (ref: 1.6)
[N/A] Readability – R1 … R4 – tool
[PASS] Art – A1 one consistent style – static/index.html:59,101,146,174 the same 1px ink/hairline underline-and-rule style ...
[PASS] Art – A2 no emoji in final art – none found in static/index.html
[PASS] Art – A3 original art – no image or branded assets; the page is type only
[FIX] Editability – E1 ... – #b4b4b4 (:113), the 0.45s fade (:156) and the type sizes ... live outside it, and only the phone-card group is marked "EDIT ME"
Top 3 fixes
1. Check the side menu between about 760px and 900px wide ... This is estimated from the code, not a screenshot ... – static/index.html:319
2. Add a second font for labels and UI ... – static/index.html:9, 16
3. Pull the leftover hard-coded values into the :root block ... – static/index.html:11-24, 113, 156
```

After the review, git still reported `nothing to commit, working tree clean` (`run2-B-gitstatus.png`).

I agree with putting the scattered color values and animation timings into one variable block. That would make it easier for me to change them later. But I do not think the page needs a second font just to satisfy the font-pairing rule. A single serif font already fits the simple look I wanted.

i have not checked the menu overlap in a browser yet, so for now I see it as a risk to investigate. If testing shows that the menu really does cover the main content, I would fix that first.

Both runs loaded the skill from a plain review request, called the tool with the right project kind, and used reference values in the report. Each returned rule results and three suggested fixes without editing files. Both also confused an inapplicable rule with a passing one: C1 in the game review, and the art rules in the tool review. That repeated mistake led to the changes in [ITERATION.md](ITERATION.md).
