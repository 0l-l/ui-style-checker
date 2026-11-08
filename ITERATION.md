# Iteration

In both demonstration runs, the checker marked rules PASS when they didn't apply, and those PASS lines had no file and line. That breaks two of the skill's own rules: N/A is for rules that don't apply, and "If you cannot cite a file and line (or the screenshot), it is NOT a PASS."

Run 1, Cozy Cat Café (game) (`screenshots/run1-B-report.png`):
```
[PASS] Color – C1 black/white or paper/ink palette – N/A for games (see C2)
```
It even wrote "N/A for games" in the evidence, then marked it PASS anyway.

Run 2, fab-finder (tool) (`screenshots/run2-B-report.png`):
```
[PASS] Art – A2 no emoji in final art – none found in static/index.html
[PASS] Art – A3 original art – no image or branded assets; the page is type only
```
The page has no art at all, so there is nothing to pass.

It didn't crash and the report looked tidy, so this was easy to miss. But a PASS with no evidence makes a project look better than it is, and it makes reports from different runs hard to compare.

My first guess was that the skill never said what N/A means. When I reread v1 of `SKILL.md`, that was wrong: v1 already defined N/A as "the rule does not apply (wrong project kind, no Chinese text, etc.)". So the definition existed. The model just didn't connect it to these two cases. Comparing what went right and wrong showed why:

The color rules only said “C1 (tool)” and “C2 (game).” By comparison, the Readability heading explicitly said “N/A for tools,” and those rules were handled correctly in both runs. That suggested the color rules needed equally direct wording.

The art rules had another ambiguity. On a text-only page, “no emoji found” could look like a pass, even though there was no art to judge. The general N/A definition did not spell out that case. And although the skill required evidence for every PASS, that instruction was near the beginning, away from the point where the agent finished the report.

## The change

Three small edits, committed as `skill v2: explicit N/A for wrong kind and no-art pages, self-check`. The file went from 82 to 85 lines. Full diff from my terminal: `screenshots/iter-diff-terminal.txt` (also `screenshots/iter-diff-agent.png`).

```
 **1. Color**
-- C1 (tool) black/white or paper/ink palette, at most one accent color
-- C2 (game) one consistent themed palette
+- C1 (tools only; N/A for games) black/white or paper/ink palette, at most one accent color
+- C2 (games only; N/A for tools) one consistent themed palette

-**5. Art**
+**5. Art** (if the page has no images, sprites or drawn art, mark A1–A3 N/A)

+## Step 4 - Self-check before sending
+Re-read every PASS line. If it has no file:line (or "screenshot"), change it to N/A or FIX.
+
 ## Output format (exactly this, nothing else)
```

The color rules now say when to use N/A, just as the Readability heading already did. The Art heading covers pages with nothing to judge. The final self-check asks the agent to revisit its PASS marks before sending the report.

These were the only skill edits. The reruns show how the revised wording behaved, though separate model sessions can also vary. The updated skill reached the Claude app through the app's skill update prompt. I checked that the loaded copy contained "Step 4 - Self-check".

## The reruns

Same prompts, word for word. Each was a new session, and nothing in the projects changed between the v1 and v2 runs.

Cozy Cat Café (game), `screenshots/iter-v2-catcafe-report.png`

```
[N/A] Color – C1 paper/ink palette, one accent – game, not a tool
[PASS] Color – C2 one consistent themed palette – style.css:2-11 (warm café creams, wood browns, one terracotta accent)
...
[FIX] Art – A1 one consistent art style – the door, bowl and seats are pixel-art SVG (sprites.js:16-63), but cats and customers are emoji (ui.js:78, ui.js:125)
[PASS] Art – A3 original art – sprites.js:16-63 hand-made pixel grids; no image files or branded assets in the repo
```

fab-finder (tool), `screenshots/iter-v2-fabfinder-report.png`

```
[PASS] Color – C1 black/white or paper/ink palette, at most one accent – static/index.html:12-13 (--paper: #ffffff, --ink: #000000, no accent color)
...
[N/A] Art – A1 one consistent art style – no images, sprites or drawn art
[N/A] Art – A2 no emoji in final art – no images, sprites or drawn art
[N/A] Art – A3 original art – no images, sprites or drawn art
```

The two failures I was targeting were corrected. Cat Café's C1 became N/A, and fab-finder's art rules all became N/A. Every PASS in both reruns had a file and line reference. Cat Café's actual art was still reviewed, the other recorded findings stayed the same, and neither review changed files (`iter-v2-*-gitstatus.png`).

But v2 dropped a row. The fab-finder v2 report goes straight from C1 to C3. C2 is missing, even though the output format says "exactly one line per check, in the order above". In v1 that row was there (`[N/A] … C2 … tool, not a game`), and in the Cat Café v2 run C1 was listed. So it happens sometimes, not always. My guess is that "(games only; N/A for tools)" reads like "skip this for tools", and the model treated skipping as allowed. Next fix: add to Step 4 something like "List every rule in order, including N/A ones; never leave a rule out." I didn't make this change because of the deadline, and I would want to rerun both projects again after it.

The tests also exposed a gap in the reference data. `get_style_reference("game")` returns only Cat Café and Bughouse Chess. My Shadow Dex and Void Hop games live in `0l-l.github.io`, which `projects.json` lists as kind `site`, so they're never included for `game`, and the "common patterns" section came back empty in every game run. The reference configuration needs separate `game` entries pointing to the actual Shadow Dex and Void Hop folders. This is also noted in `README.md`.

In these runs, spelling out applicability beside the rule worked better than relying on the general N/A definition. The final citation check also helped: every PASS in the two v2 reports had a source location.

That is a useful improvement, but it is only evidence from two reruns. The missing C2 row shows why the next check needs to cover completeness as well as citations. A tidy report can still be wrong; the rule-by-rule results matter more than how convincing the summary sounds.
