# AGENTS.md — OW_tool Codex instructions

## Mission
Maintain a Windows/Python tool that captures Overwatch scoreboards on TAB and ultimately retains only the last valid scoreboard screenshot per match. Preserve working behavior while improving map recognition and maintainability.

## Read first
1. Read `docs/DEVELOPMENT_HANDOFF.md` for decisions, measured results, unresolved issues and implementation status.
2. Inspect the **actual repository** before modifying anything (`main.py`, `capture/`, `detector/`, `logger/`, tests and requirements). The handoff is historical context, **not** proof that a proposed change is present in the working tree.
3. If code differs from the handoff, report the discrepancy and use code as the source of truth; ask before making changes that alter agreed behavior.

## Non-negotiable behavior
- Target environment: Windows, Overwatch fullscreen **1920×1080**, fixed UI scale. Do not add active-window-only capture or responsive ROI support unless asked.
- Trigger processing **once on TAB key-down**, then wait for key-up; never capture only on key release or repeatedly while held.
- `CaptureManager` owns the Overwatch foreground check (`is_overwatch_active`) and capture coordination; `GameCapture` captures frames; `ScoreboardLocator` detects the scoreboard. Keep responsibilities separated.
- Reject non-scoreboard or invalid/dark frames before updating the per-match buffer. Preserve the last good frame.
- Same match: replace buffered screenshot with the latest valid one. Different match: save previous buffered screenshot and start a new buffer. On graceful exit, flush the final buffered screenshot (Ctrl+C / `finally`).
- Keep a runnable, minimal version working at all times. Prefer focused patches over broad rewrites.
- Do not reintroduce visual detection of the `|` delimiter between mode and map: it produced false positives on letters (L/R). Keep the full map ROI.
- Avoid assuming identical map names necessarily imply the same match across arbitrary time spans. If improving matching, discuss edge cases and preserve existing behavior until approved.

## Current OCR benchmark contract
- Input images: `captures/ok/*.png`.
- Ground truth: `captures/ok/map_name.txt`, one `filename.png<TAB>MAP NAME` per line.
- Map-name ROI: `x=1323, y=13, width=420, height=42`; **do not narrow it**.
- OCR test uses Tesseract/pytesseract (`eng`, `--oem 3 --psm 7`) and RapidFuzz dictionary matching (historically `fuzz.WRatio`).
- Seven preprocessing variants: `gray`, `gray_x4`, `clahe`, `clahe_x4`, `otsu`, `adaptive`, `lanczos`.
- Latest reported evaluation on 40 labeled screenshots: all variants **except `adaptive`** achieved **40/40**; `adaptive` achieved **37/40**. This is a benchmark on this sample, not a universal accuracy guarantee.
- The dictionary **must contain `NEW QUEEN STREET`**. Preserve accents and punctuation in display names.
- Do not confuse a RapidFuzz match score with calibrated OCR confidence; do not silently impose a score cutoff (e.g. 80) without evaluating the labeled set.

## Configuration refactor (next agreed task)
- Prefer `config/settings.py` with simple grouped classes `OCRConfig`, `ROIConfig`, `ScoreboardConfig`, `MatchConfig`; `config/maps.py` with `MAP_NAMES`; and `config/__init__.py`.
- Typical import: `from config.settings import OCRConfig, ROIConfig`; `from config.maps import MAP_NAMES`.
- Move existing literals to configuration without changing behavior. Verify the actual values and call sites first; earlier example values were sometimes proposals, not confirmed production settings.
- Do not switch to YAML/JSON or dataclasses without user approval. Preserve public interfaces unless necessary.

## Working style
- Communicate in Japanese, give concrete file-level changes and complete code when requested.
- Explicitly distinguish **implemented**, **benchmarked**, **proposed**, and **not yet verified**.
- Provide a short test plan and results after changes. Do not claim tests ran without running them.
- Keep future work (multilingual player-name OCR, role detection, match metadata) separate from the current narrow deliverable.
