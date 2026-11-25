# Validation notes: defra-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/defra-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head daa98da. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

22/24 valid (91.7%), mean field score 0.958, **easy 5/5**. By category: boundary_twin 6/6, distractor 2/2, easy 5/5, flag 1/3, hidden_clause 2/2, multi_rule 4/4, refusal 2/2.
$0.00113 billed per run, 8,580 prompt tokens per call, 3.96 calls per run;
0 of 24 runs would exceed the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| bluebell-dene | flag | BOOK EgyptAir business, WORK_ON_ARRIVAL; key FLAG | model slip | It saw the open question and presumed an answer: "5 hours is between 5 and 10 (inclusive presumably)". The 300-minute journey is not "less than 5 hours" (line 204), and whether "between 5 hours and 10 hours" (line 205) includes 5 hours is the unclear phrase; it booked business for work on arrival without weighing the other reading. The twins hawthorn-ings and hornbeam-sett passed. |
| campion-wold | flag | BOOK KLM economy, UPGRADE_NOT_ELIGIBLE; key FLAG | model slip | "The flight is under 5 hours (205 minutes of flying time)". Both itineraries connect: 315 and 320 minutes from first departure to last arrival. It never weighed how line 204 measures a journey. The twins nightjar-holm and ouzel-scarp passed. |

## Fixes

None. All 2 failures are model slips; no key was widened and no record changed.

## Q2

Unchanged: the always-cheapest agent passes **6/24 (25%)**.

## Re-score at the head (stored answers)

22/24 (no key changed). No re-run is required.

## Checks (at the notes commit)

`uv run pytest -q` (211 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical `rules.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
