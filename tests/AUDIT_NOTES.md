# Audit notes: defra-flight-policy (2026-11-25)

This file is under tests/ because stock `nanoagent plugin inspect` rejects extra files at the plugin root.

This is an independent audit of the build at d40100b. I re-derived every answer from the frozen handbook
(`src/plugin/data/policy.txt`, lines 178-212 for air, 84-98 for the principles) and from what the agent sees: the
task instructions, the `get_trip` record and the pinned `search_flights` listing, dumped for each scenario. I did
not use `rules.py` to derive them. I then compared each answer with every accept set (decision, offer, cabin, reason,
approver, clause). The standard was WAVE3_BUILD_BRIEF's 12 lessons, MASTER_PLAN section 4, EDGE_CASES sections
1-3 and 5, and the fedex-office, goodman-networks, hillrom and georgia-sao audits.

**Verdict: pass after fixes.** The key was right on all 21 non-flag scenarios, and the 3 flags are genuine. The
defects were one gap in the agent-visible conventions, one clause accept set and one request detail. No decision,
offer, fare or time changed.

## Defects found and fixed

| # | Scenario(s) | Problem | Fix |
|---|---|---|---|
| 1 | hawthorn-ings / hornbeam-sett (299/301), kingcup-beck / merlin-garth (600/601), bluebell-dene (300) | Lines 204-212 measure "journeys", and the handbook itself mentions "travel to and from an airport" (lines 183-184). A model that counts door to door would put 299 above 5 hours: it would book business in hawthorn-ings. It would put 600 over 10 hours: it would book business in kingcup-beck, using the manager's conditional yes. It would also book business in bluebell-dene. Each is a false failure. The world has no transfer times, and the agent cannot call `booking_requirements`, so nothing it sees settled this. | Added to the task instructions' conventions line, and to `rules.CONVENTIONS` (shown by booking_requirements): "No time is counted for getting to or from an airport: a nonstop flight's length is its scheduled minutes." This rules out airport transfers. It says nothing about the wait between connecting flights, so the campion-wold flag (flying time against first departure to last arrival) stays open. The lint passes: no number or 4-word phrase of a must_keep clause. |
| 2 | teasel-croft | The clause accept set was `PRINCIPLES`, `AIR`. Every other air decision also accepts `RAIL_AND_AIR`, the contents-listed section that holds the "Air" sub-heading. A model that cites the air rules for this booking can fairly name either one (lesson 5). | `rules.safety` accepts `PRINCIPLES`, `AIR`, `RAIL_AND_AIR`. The baseline cannot rise, because the reason must still be TRAVELLER_SAFETY. |
| 3 | teasel-croft | Today is the travel date and the world has no clock, so a model could ask whether the 09:10 "first flight" has already left. | The request adds "it's 06:30 here now". The world is unchanged. |
| - | campion-wold (wording only) | The answer-key explanation and the design note called the elapsed reading "door to door". After fix 1 that wording clashes with the convention. | Both now say "from first departure to last arrival". The accept sets are unchanged. |

## Builder's unsure list, settled

- **299/301 and 600/601 measured in scheduled minutes, against "journeys":** this was a real risk of false failure.
  Fixed by defect 1, with a convention rather than wider accept sets. Accepting business at 299 or 600 would make
  each twin pair meaningless. It would also accept a booking that is wrong on the plain reading.
- **teasel-croft (book the dearer first flight, hold for prior approval, or book a cheaper later flight):** the
  text settles it as BOOK the 09:10 TK flight (£325).
  - A hold is wrong. Line 195 requires prior approval, but lines 92-98 cover this case exactly: the traveller feels
    unsafe and "it is not practical to seek prior approval before taking additional steps. In such cases approval
    can be obtained retrospectively." The record says the manager is on leave and no approver can be reached, so a
    hold would leave the traveller in place with nobody to answer it.
  - The cheaper later flights (BA 13:45 £274, TK 18:30 £218) are not the "lowest practical fare" (line 187). The step
    the safety clause covers is leaving now, and the traveller asks for the first flight because they feel unsafe.
    Booking a flight 4 or 9 hours later defeats that step.
  - Economy is right: 235 minutes is less than 5 hours (line 204). The approver is MANAGER (retrospective) or NONE.
    The key is unchanged, apart from fixes 2 and 3.
- **sedum-howe (first class under the overseas exception, relying on a record field):** clear enough, so no change.
  - The request says the airlines sell "only economy and what they call first, which the booking agent says is the
    same seat as business class elsewhere". The record's `first_is_business_grade` field states the same fact. The
    search shows no business cabin, the origin is JFK (the traveller is "in New York this week", on a US visit) and
    the flight is a US internal one. That is the case lines 197-203 describe, including "overseas internal flights".
  - The business rules then apply: 370 or 375 minutes is between 5 and 10 hours, and the traveller goes straight
    into the meeting (line 209). Book the cheapest such cabin, AA first at £1,180.
  - The residual risk is a model that stops at "complete ban" (line 196). That would be a reading error, not an
    ambiguity, because the exception follows in the next sentence. Economy is not accepted, because the policy
    allows what the traveller asked for.

## Re-derivation, scenario by scenario (all agree with the key after the fixes)

- Easy (5):
  - bracken-stile: LH £98 is sold out, so BA £112 (lands 11:45, before 15:00).
  - curlew-hithe: economy asked, BA £612.
  - dipper-combe: the health letter meets the medical case (210), so VS business £2,360.
  - foxglove-shingle: IB via MAD £587.
  - gentian-sike: EDI-CDG is not within mainland GB; KL via AMS £143 lands the evening before the meeting.
- Boundary twins (6):
  - hawthorn-ings (299 min): economy MS £289; business declined.
  - hornbeam-sett (301 min): work on arrival, so MS business £1,315.
  - kingcup-beck (600 min): not over 10 hours, and none of the three cases holds (an economy seat is free, the
    dialogue starts two days later, no medical grounds), so CA economy £546. The manager's yes is conditional on the
    policy. Both readings of "between" give economy.
  - merlin-garth (601 min): over 10 hours with the manager's approval, so CA business £2,980.
  - nightjar-holm: 425 min with the 21:30 session straight from the airport, so EK business £1,980.
  - ouzel-scarp: the session is the next morning, so EK economy £412.
- Multi-rule (4):
  - pipit-moss: the director's exception (180-181) and the manager's approval are on file, so BA 09:40 £78.
  - quillwort-ness: first is banned and a genuine business cabin exists (202-203); 405 min with work on arrival,
    so QR business £1,890.
  - ragwort-lea: every economy and premium economy seat is sold out and the date is fixed (207-208), so AI business
    £2,210.
  - samphire-dyke: EK and SQ land after 14:00 on 1 Dec, so BA £615.
- Hidden clause (2): sedum-howe and teasel-croft (above).
- Distractors (2):
  - thrift-gill: Dublin is not mainland GB, so EI 10:50 £74.
  - vervain-knowe: 135 min means economy only; Standard Premier is a Eurostar rule. BA 08:05 £142.
- Refusals (2):
  - wagtail-brow: the director refused the exception (180-181).
  - whinchat-bield: a personal wedding trip is not official business (40-43, 69-71).
- Flags (3):
  - bluebell-dene: 300 min is not "less than 5 hours", and the text does not say whether "between" takes in 5
    hours. Each reading's offer is accepted.
  - campion-wold: 205 flying minutes against 315/320 elapsed straddles 5 hours. Each reading's offer is accepted.
  - woodruff-staithe: over 10 hours, and the manager's answer on business is awaited, so hold SA business £3,180
    for MANAGER.

Other checks:
- Twins differ in one fact each: the minutes (both numeric pairs), work on arrival against the next morning, and
  the director's answer.
- No request repeats rule wording. vervain-knowe's "value for money" is the intended distractor.
- The decline sentence is in the instructions.
- Every request that names a premium cabin has a fallback.
- Every case states when the business starts.

Baselines: always-cheapest is unchanged: **MAX_PASS_ALWAYS_LOWEST 6 -> 6** (bracken-stile, curlew-hithe,
foxglove-shingle, gentian-sike, pipit-moss, thrift-gill; 25%). Always-flag passes 2.

## Acceptance (after the fixes)

```
uv run pytest -q                               211 passed
uv run ruff check .                            All checks passed!
uv lock --check                                Resolved 42 packages
python3 ../_template/check_shared.py .         : ok
<stock venv>/bin/python ../_template/tools/stock_verify.py .   24 scenarios, 0 failures
<stock venv>/bin/nanoagent plugin inspect .    exit 0
```
