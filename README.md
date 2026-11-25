# Defra Flight Policy

**Source of the handbook:** https://www.contractsfinder.service.gov.uk/Notice/Attachment/a8d95d45-a849-47bd-937a-c1095f833b14. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with the Department for Environment, Food and Rural Affairs.** The handbook is the department's
*Staff Expense (Travel & Subsistence) Policy* v2.0 (published August 2021), a PDF released with a UK Contracts Finder
notice and marked "Classification: OFFICIAL" (unrestricted), bundled verbatim for research. Its public URL is not
recorded locally; confirm it before this plugin is published (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the department's real
travel policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 3,612 words, 468 lines, 25,654 bytes, sha256 `28c67507...0cc84`,
equal to `pilot_work/originals/defra/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule.
The page footer "Published: Aug '21" survives mid-text at page breaks (for example line 193, inside the air class
table); it is kept, and quotes use the text as it is. Under stock NanoAgent the agent does not see the policy: the
plugin then runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork
(github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt: `harness.policy: full` adds
all of it, and the selection methods add parts of it. These plugins are meant to run with
`query: instructions+input`, so a selector sees the traveller's request.

**Size.** At 1.33 tokens a word the policy alone is about 4,800 tokens; on the Thornton/NJC calibration (about 0.2
tokens a character plus 1,800) the first `full` call is about 7,000 input tokens. A run makes 3 calls (`get_trip`,
`search_flights`, `submit`) of about 7,000, 7,300 and 8,000: about 22,000 input tokens per run, plus about 8,500 for
the final message, far under the hosted cap of 65,536.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (every case buys one one-way ticket),
  then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list plus
  six codes of this policy (`DOMESTIC_AIR_NOT_PERMITTED`, `POLICY_EXCEPTION_APPROVED`, `WORK_ON_ARRIVAL`,
  `FIRST_CLASS_BANNED`, `FIRST_AKIN_TO_BUSINESS`, `TRAVELLER_SAFETY`) and fifteen decoy codes from other handbooks'
  rules. Fares are in pence (`fare_cents` in hundredths of the currency; `currency: GBP`).
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Reasons on a declined request.** When the booking is not what the traveller asked for, the reason gives why the
  request is declined: business or premium economy declined on the length of the journey accepts
  `UPGRADE_NOT_ELIGIBLE` or `LONG_FLIGHT_CONDITION_NOT_MET` (not `LOWEST_FARE`); first class declined
  (`quillwort-ness`) accepts `FIRST_CLASS_BANNED` or `UPGRADE_NOT_ELIGIBLE`.
- **No hidden facts:** no scenario has `answer_key_inputs`.

| Scenario | Category | Expected decision (offer; cabin) | Frozen lines |
|---|---|---|---|
| `bracken-stile` | easy | BOOK (mid-economy; ECONOMY): cheaper fare sold out | 187, 195, 204 |
| `curlew-hithe` | easy | BOOK (british-economy; ECONOMY): economy asked on 790 minutes | 187, 195, 211-212 |
| `dipper-combe` | easy | BOOK (virgin-business; BUSINESS): health letter, 460 minutes | 187, 195, 205-210 |
| `foxglove-shingle` | easy | BOOK (madrid-economy; ECONOMY): connection via Madrid | 187, 195 |
| `gentian-sike` | easy | BOOK (amsterdam-economy; ECONOMY): connection lands the evening before | 187, 195, 204 |
| `hawthorn-ings` | boundary_twin | BOOK (egyptair-economy; ECONOMY), 299 minutes | 187, 195, 204, 205-210 |
| `hornbeam-sett` | boundary_twin | BOOK (egyptair-business; BUSINESS), 301 minutes, work on arrival | 187, 195, 204, 205-210 |
| `kingcup-beck` | boundary_twin | BOOK (airchina-economy; ECONOMY), 600 minutes | 187, 195, 205-212 |
| `merlin-garth` | boundary_twin | BOOK (airchina-business; BUSINESS), 601 minutes, manager approved | 187, 195, 205-212 |
| `nightjar-holm` | boundary_twin | BOOK (emirates-business; BUSINESS): straight to work | 187, 195, 205-210 |
| `ouzel-scarp` | boundary_twin | BOOK (emirates-economy; ECONOMY): work starts the next morning | 187, 195, 205-210 |
| `pipit-moss` | multi_rule | BOOK (mid-economy; ECONOMY): London-Edinburgh, director's exception | 180-184, 187, 195 |
| `quillwort-ness` | multi_rule | BOOK (qatar-business; BUSINESS): first asked, genuine business exists | 187, 195-210 |
| `ragwort-lea` | multi_rule | BOOK (airindia-business; BUSINESS): no economy seat, date fixed | 187, 195, 205-210 |
| `samphire-dyke` | multi_rule | BOOK (british-economy; ECONOMY): cheaper flights land too late | 187, 195 |
| `sedum-howe` | hidden_clause | BOOK (american-first; FIRST): overseas "first" akin to business | 187, 195-210 |
| `teasel-croft` | hidden_clause | BOOK (turkish-early-economy; ECONOMY): unsafe, approval afterwards | 92-98, 195, 204 |
| `thrift-gill` | distractor | BOOK (aerlingus-late-economy; ECONOMY): Dublin is not mainland Great Britain | 187, 195, 204 |
| `vervain-knowe` | distractor | BOOK (morning-economy; ECONOMY): premium economy asked, Eurostar rule nearby | 187, 195, 204 |
| `wagtail-brow` | refusal | REFUSE: London-Edinburgh, director refused the exception | 180-184, 187, 195 |
| `whinchat-bield` | refusal | REFUSE: personal trip | 40-43, 69-71 |
| `woodruff-staithe` | flag | FLAG_FOR_APPROVAL (southafrican-business; BUSINESS), APPROVAL_REQUIRED, MANAGER | 187, 195, 211-212 |
| `bluebell-dene` | flag | FLAG_FOR_APPROVAL (egyptair-business or egyptair-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 187, 195, 204, 205-210 |
| `campion-wold` | flag | FLAG_FOR_APPROVAL (frankfurt-business or amsterdam-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 86-91, 187, 195, 204, 205-210 |

Every accepted reason, approver and section per case is in the scenario files and `tests/BUILD_NOTES.md`.

**Duration (`rules.over`).** Lines 204-212: "less than 5 hours" economy only (strict); "between 5 hours and 10 hours"
business in three listed cases (no lower-class seat with the date fixed, work immediately on arrival,
disability/medical grounds); "over 10 hours" business subject to a manager's or approver's approval (strict). A
nonstop's journey is its scheduled minutes. For a connection the text does not say whether a journey is the flights'
minutes or the elapsed time with the wait; when the two straddle a limit the answer is unclear (`None`), which only
`campion-wold` uses. Exactly 5 hours is in a gap ("between" is not confirmed inclusive): `bluebell-dene`. Exactly
10 hours is not "over 10 hours" on any reading, so with none of the three cases it is economy (`kingcup-beck`).

**Approvers.** Every booking relies on the manager's prior approval of the air travel (line 195), on file, so it
accepts `MANAGER` and `NONE` (SYNC_NOTES 4'); `pipit-moss` also accepts `DIRECTOR`. A refusal accepts `NONE` and the
roles on file. The approval hold `woodruff-staithe` accepts only `MANAGER`. A hold over unclear words accepts
`NOT_NAMED` or `MANAGER` (lines 86-88: travel outside the policy needs line management's prior approval).

Degenerate agents (`tests/test_verifier.py`): always holding the right offer as unclear passes 2 cases (the two
unclear flags); always booking the cheapest seat with `LOWEST_FARE`, `NONE` and the right section passes 6.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, date, when the business starts, purpose, requested cabin, the facts the class rules turn on, and the sign-offs asked for with their outcome | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-defra-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, reason codes
  and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design choices, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/defra-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
