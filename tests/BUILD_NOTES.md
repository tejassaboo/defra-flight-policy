# Build notes: defra-flight-policy (wave 3, 2026-11-24)

Built from `_template` with `instantiate.py` (slug `defra`, `--task-id book-defra-flight`, `--currency GBP`,
`--background 0`, `--scenarios 24`). Frozen handbook: `pilot_work/originals/defra/frozen/defra_policy.txt`, 3,612
words (under 10,000, so 24 scenarios), 468 lines, sha256 `28c67507...0cc84`. The lead was away, so each decision was
taken without asking and is recorded here.

## 1. What the handbook supports

Mandatory or checkable flight clauses (frozen line numbers):

| Lines | Clause | Operator / force | Used by |
|---|---|---|---|
| 40-43, 69-71 | only expenses incurred in the course of official business | mandatory ("must") | whinchat-bield |
| 86-91 | travel outside the policy: prior approval from line management | should, exceptional | unclear holds (approver) |
| 92-98 | feeling unsafe and prior approval not practical: approval retrospectively | permissive | teasel-croft |
| 180-181 | no air travel between locations on mainland England, Wales and Scotland unless a director grants an exception | "not permitted unless" | pipit-moss, wagtail-brow; thrift-gill, gentian-sike (not mainland) |
| 182-184 | rail preferred where travel is unavoidable | soft (never a refusal by itself) | wagtail-brow (reason), thrift-gill (aside) |
| 187 | the lowest practical fare within the permitted class | should | every booking; samphire-dyke (late arrivals are not practical) |
| 195 | all air travel requires prior approval from a manager or approver | mandatory | every booking has it on file (approver MANAGER or NONE) |
| 196-203 | complete ban on first class; overseas, an airline "first" akin to business with no genuine business class may be used under the business rules | ban plus exception | quillwort-ness, sedum-howe |
| 204 | journeys of "less than 5 hours": economy only | strict | hawthorn-ings, vervain-knowe, and others |
| 205-210 | "between 5 hours and 10 hours": business where (a) no lower-class booking and timing/date fixed, (b) work immediately on arrival, (c) disability/medical grounds | three cases, any one | dipper-combe (c), ragwort-lea (a), hornbeam-sett, nightjar-holm, quillwort-ness, sedum-howe (b) |
| 211-212 | "over 10 hours": business subject to approval from a manager or approver | strict, approval | merlin-garth, woodruff-staithe |

Not used: the booking-agent rule (line 169: the world has only the approved agent's offers), the Tickets on Departure
supplement (rail), "travel should be avoided where possible" (soft), the rail, car, taxi, hotel, subsistence and
allowance sections (only as distractors). Line 435 (prior approval for all foreign travel) duplicates line 195 here.
No rule on several travellers on one flight and none on overnight stops: the `multi_traveller` overlay is not
required (`plugin_spec.OVERLAY_MINIMUMS`). No round-trip case: every case buys one one-way ticket and the trip
record has no `return_date` field.

## 2. Unclear points and how they are handled

- **"between 5 hours and 10 hours" at exactly 5 hours** (line 205; EDGE_CASES section 2: "between" is inclusive only
  if the handbook confirms it, and it does not). Flag `bluebell-dene`: 300-minute nonstops, traveller works on
  arrival. Twins `hawthorn-ings` (299: "less than 5 hours" is clear, economy) and `hornbeam-sett` (301: clearly in the
  band, business). The hold accepts the business or the economy fare (each reading's offer).
- **How a "journey" with a connection is measured** (line 204, flying time or first departure to last arrival).
  Flag `campion-wold`: flights adding to 205 minutes, elapsed 315-320, traveller works on arrival. Twins
  `nightjar-holm` (business) and `ouzel-scarp` (economy). Nowhere else does a case depend on it: every other
  connection (foxglove-shingle, gentian-sike, samphire-dyke) is an economy request, and `rules.business` raises if
  offers in one case fall in different bands.
- **Exactly 10 hours** is not a flag: 600 minutes is not "over 10 hours" on any reading, and with none of the three
  cases both readings of "between" give economy (`kingcup-beck`). With one of the cases met at 600 the readings would
  split; `rules.band` raises there and no scenario uses it.
- **The three cases of lines 206-210** are read as "any one suffices" (bullets with no "and"; requiring all three,
  disability included, is not a sensible reading). Every business case meets exactly one.
- **Approval required** (`woodruff-staithe`): over 10 hours, business asked, the manager approved the air travel but
  has not answered on business class: hold the cheapest business fare for MANAGER. Twins `merlin-garth` (approved:
  book business) and `kingcup-beck` (600 minutes: economy).
- **The manager's "yes to business class if the policy allows it"** (kingcup-beck, merlin-garth) is conditional on
  purpose, so at 600 minutes it is not an outside-the-policy approval under lines 86-88. The note is in the sign-off
  and the request, identically in both twins.
- **Mainland flights with no director's answer** (refuse or hold?) are avoided: the director either granted
  (`pipit-moss`) or refused (`wagtail-brow`) the exception; `rules.solve` raises otherwise.

## 3. Choices made without asking

1. Approvers: every booking accepts `MANAGER` and `NONE` (the line 195 approval is on file, SYNC_NOTES 4'), plus any
   other role on file (`pipit-moss`: `DIRECTOR`). Refusals accept `NONE` and the roles on file (wagtail-brow:
   `DIRECTOR`, `MANAGER`; whinchat-bield: `MANAGER`, whose sign-off is for annual leave). The approval hold accepts only
   `MANAGER`. Unclear holds accept `NOT_NAMED` or `MANAGER`, and `APPROVAL_REQUIRED` beside `UNCLEAR_POLICY_TEXT`.
2. One approver role `MANAGER` for the handbook's "manager or approver"; the trip records name the line manager.
3. Declined requests (lesson 12): business/premium economy declined on duration accepts `UPGRADE_NOT_ELIGIBLE` or
   `LONG_FLIGHT_CONDITION_NOT_MET`, never `LOWEST_FARE`; first declined accepts `FIRST_CLASS_BANNED` or
   `UPGRADE_NOT_ELIGIBLE`, not the case code that permits business. `pipit-moss` accepts `LOWEST_FARE` beside
   `POLICY_EXCEPTION_APPROVED` (nothing is declined). `wagtail-brow` accepts `DOMESTIC_AIR_NOT_PERMITTED`,
   `RAIL_PREFERRED`, `NO_COMPLIANT_OFFER`. `whinchat-bield` accepts `PERSONAL_TRAVEL_NOT_COVERED` or
   `OUTSIDE_POLICY_SCOPE`.
4. Clauses: air decisions accept `RAIL_AND_AIR` ("Rail and air travel, including class of travel", which holds lines
   178-187) and `AIR` (the "Air" heading over the class table and lines 195-212). The safety case accepts
   `PRINCIPLES` or `AIR`; the personal refusal `INTRODUCTION`, `PURPOSE`, `PRINCIPLES` or `SCOPE`; unclear holds add
   `PRINCIPLES` (lines 86-88).
5. `teasel-croft` keys the earliest flight (09:10, dearer): the traveller asks for the first flight because they feel
   unsafe, and lines 92-98 cover "additional steps" without prior approval. The cheaper later flights are not keyed.
6. `sedum-howe`: the trip record's `first_is_business_grade` gives the booking agent's statement that the airlines'
   "first" on JFK-LAX is a business-class product (the quote test forbids outside knowledge of airline cabins). Only
   economy and first are sold. The origin is overseas (US), as line 197 requires.
7. `ragwort-lea`: the request says the traveller cannot travel on any other day and the record's `date_fixed` is
   true, so "the timing or date of the journey cannot be changed" holds (lesson 8: no other date is searched).
8. Background offers: 0 on every search (handbook.json and each pinned search), so the agent sees exactly the pinned
   offers and an unpinned search lists nothing.
9. Every trip record gives `business_starts`, and every keyed offer lands before it (lesson 4); in samphire-dyke the
   cheaper offers land after it, which is the point of the case.
10. Decoy reason codes (grepped; no subject in the text): WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED,
    NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING,
    EXTENDED_TRAVEL_SAVINGS, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED
    (the text's only "double" is a lodging "double commitment"), PRIVATE_AIRCRAFT_NOT_APPROVED,
    CANDIDATE_TRIP_NOT_COVERED, SAME_CLASS_AS_CUSTOMER, COMPANION_TRAVEL_AUTHORIZED, CHOSEN_AIRLINE_AT_LOWEST_FARE,
    FLEXIBLE_FARE_JUSTIFIED. Approver decoys: TRAVEL_AGENCY, VICE_PRESIDENT, CHIEF_EXECUTIVE, HUMAN_RESOURCES.
11. Airports: the shared world's mainland-GB airports are LHR, LGW and EDI only, so the mainland cases are London to
    Edinburgh and the "not mainland" distractor is Dublin (see section 7).

## 4. Mix and overlays

5 easy, 6 boundary_twin, 4 multi_rule, 2 hidden_clause, 2 distractor, 2 refusal, 3 flag (12.5%). Decisions: 19 BOOK
(7 business-grade, 1 of them first; 12 economy), 2 REFUSE, 3 FLAG. Overlays: multi_leg 4, date_arithmetic 2 (month_end
1), personal_travel 1, dearer_option 11, upgrade_not_taken 2, outside_air_section 2. Numeric twin pairs: 299/301
minutes (the 5-hour line) and 600/601 (the 10-hour line); fact pairs: work on arrival or the next morning
(nightjar-holm/ouzel-scarp), the director's answer (pipit-moss/wagtail-brow, refusal side in category refusal).
Degenerate agents: always-flag passes 2 (bluebell-dene, campion-wold); always-cheapest passes 6 (bracken-stile,
curlew-hithe, foxglove-shingle, gentian-sike, pipit-moss, thrift-gill), `MAX_PASS_ALWAYS_LOWEST = 6`.

## 5. Independent blind read (non-flag scenarios)

Re-derived from the frozen text and the tool outputs only (the `get_trip` record and the `search_flights` listing,
dumped per scenario), not from rules.py, then compared with `expected`.

| Scenario | My reading from text + offers | Agrees |
|---|---|---|
| bracken-stile | 75 min, under 5 h: economy (204); LH 07:00 £98 sold out; cheapest seated BA 09:30 £112, lands 11:45 before 15:00; manager approval on file (195) | yes |
| curlew-hithe | 790 min would allow business with approval (211-212) but economy asked: cheapest BA £612 | yes |
| dipper-combe | 460/465 min, between 5 and 10 h; occupational health letter = medical grounds (210): cheapest business VS £2,360 | yes |
| foxglove-shingle | economy, connection welcome: IB via MAD £587 cheapest, lands 9 March, workshop 11 March | yes |
| gentian-sike | EDI-CDG not mainland GB; KL via AMS £143 lands 19:50 the evening before the 09:30 meeting: practical and cheapest | yes |
| hawthorn-ings | 299 min is less than 5 h: economy only despite work on arrival; MS economy £289; business declined | yes |
| hornbeam-sett | 301 min: between 5 and 10 h; straight into the talks = work immediately on arrival (209): MS business £1,315 | yes |
| kingcup-beck | 600 min not over 10 h; no case of 206-210 (dialogue two days later, economy free, no medical); manager's yes is conditional: CA economy £546 | yes |
| merlin-garth | 601 min over 10 h; business approved by the manager (211-212): CA business £2,980 | yes |
| nightjar-holm | 425 min, between; goes straight from the airport to the 21:30 session (lands 18:50/20:25): EK business £1,980 | yes |
| ouzel-scarp | 425 min, between; work starts next morning, economy free: EK economy £412, business declined | yes |
| pipit-moss | LHR-EDI is within mainland GB (180-181); director's exception and manager's approval on file; 70 min economy; BA 09:40 £78 lands 10:50 | yes |
| quillwort-ness | first banned (196-197); genuine business on both airlines, so the "akin" exception fails (202-203); 405 min + work on arrival: QR business £1,890 | yes |
| ragwort-lea | 545 min; every economy and premium economy seat sold out; the summit fixes the date: business (207-208), AI £2,210 | yes |
| samphire-dyke | opening 14:00 on 1 Dec: EK (£528, lands 15:25) and SQ (£589, lands 17:40) are late, not practical; BA £615 lands 08:15 | yes |
| sedum-howe | overseas (JFK-LAX), only economy and "first", agent says first is business-grade, no genuine business: first usable under business rules; 370/375 min + work on arrival: AA first £1,180 | yes |
| teasel-croft | feels unsafe, no approver reachable: retrospective approval (92-98); first flight TK 09:10 £325 (later ones cheaper); 235 min economy | yes |
| thrift-gill | Dublin is not mainland GB, no exception needed; 60 min economy; EI 10:50 £74 lands 11:50 before 13:00 | yes |
| vervain-knowe | 135 min, less than 5 h: economy only; Standard Premier rule (221-222) is Eurostar; BA 08:05 economy £142 | yes |
| wagtail-brow | LHR-EDI within mainland GB, director refused the exception: no flight (180-181); refuse | yes |
| whinchat-bield | sister's wedding on leave: not official business (40-43, 69-71): refuse | yes |

21 of 21 non-flag scenarios agree. Points the read raised and fixed before commit: `ragwort-lea`'s request first
said "I can't fly any later", which leaves an earlier day open against "the timing or date ... cannot be changed";
it now says the traveller cannot travel on any other day. `quillwort-ness` first gave the traveller a Director title,
which adds nothing to the class rules but invites a seniority reading; it is now "Lead Negotiator".

Residual risks (not fixed):
- A reader may count a "journey" door to door, airport transfers included (lines 183-184 speak of "travel to and from
  an airport" for rail against air). The world gives no transfer times, and the quote test rules out guessing them,
  so nonstops are measured by scheduled minutes; a model could still balk at 299/301 or 600/601.
- `teasel-croft`: a model may hold the flight for line 195's prior approval, or book the cheapest later flight.
  Lines 92-98 say approval "can be obtained retrospectively" and the request asks for the first flight.
- `sedum-howe`: a model may refuse anything labelled first (line 196 "complete ban") without reading on to 197-203.

## 6. Hosted-cap estimate

Full-handbook prompt: 25,654 bytes (the table of contents' dot leaders are most of the extra); about 4,800 tokens at
1.33 a word, about 7,000 on the Thornton/NJC calibration (0.2 a character plus 1,800). A 3-call run is about 22,000
input tokens before the final message (about 30,000 with it): far under the 65,536 cap.

## 7. Template change requests

- **Airports for UK handbooks.** The shared world has only LHR, LGW and EDI in Great Britain. Defra's mainland rule
  (lines 180-181) would be tested better with Manchester (MAN), Glasgow (GLA), Birmingham (BHX), Aberdeen (ABZ),
  Inverness (INV), Newcastle (NCL), and above all Belfast (BFS, Northern Ireland: in the UK but not mainland Great
  Britain, the case the clause's wording turns on) and Jersey (JER, not in the UK). BA's hubs touch all of them, so
  no hub change is needed. Worked around: London-Edinburgh for the mainland cases and Dublin for "not mainland".
- None else. Observation: the skeleton's `get_trip` tool description named "earlier flights" (Thornton's record); it
  is a per-plugin file (`nanoagent.yaml`) and was reworded here.

## 8. Acceptance outputs

```
$ uv run pytest -q
211 passed in 2.66s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 5ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .
ok (exit 0)
$ nanoagent plugin pack . /tmp/defra-flight-policy.tar.gz
packed . into /tmp/defra-flight-policy.tar.gz (155769 bytes)
$ python ../_template/tools/stock_verify.py .
bluebell-dene        right=True score=1.00 identical=True wrong-decision-rejected=True
bracken-stile        right=True score=1.00 identical=True wrong-decision-rejected=True
campion-wold         right=True score=1.00 identical=True wrong-decision-rejected=True
curlew-hithe         right=True score=1.00 identical=True wrong-decision-rejected=True
dipper-combe         right=True score=1.00 identical=True wrong-decision-rejected=True
foxglove-shingle     right=True score=1.00 identical=True wrong-decision-rejected=True
gentian-sike         right=True score=1.00 identical=True wrong-decision-rejected=True
hawthorn-ings        right=True score=1.00 identical=True wrong-decision-rejected=True
hornbeam-sett        right=True score=1.00 identical=True wrong-decision-rejected=True
kingcup-beck         right=True score=1.00 identical=True wrong-decision-rejected=True
merlin-garth         right=True score=1.00 identical=True wrong-decision-rejected=True
nightjar-holm        right=True score=1.00 identical=True wrong-decision-rejected=True
ouzel-scarp          right=True score=1.00 identical=True wrong-decision-rejected=True
pipit-moss           right=True score=1.00 identical=True wrong-decision-rejected=True
quillwort-ness       right=True score=1.00 identical=True wrong-decision-rejected=True
ragwort-lea          right=True score=1.00 identical=True wrong-decision-rejected=True
samphire-dyke        right=True score=1.00 identical=True wrong-decision-rejected=True
sedum-howe           right=True score=1.00 identical=True wrong-decision-rejected=True
teasel-croft         right=True score=1.00 identical=True wrong-decision-rejected=True
thrift-gill          right=True score=1.00 identical=True wrong-decision-rejected=True
vervain-knowe        right=True score=1.00 identical=True wrong-decision-rejected=True
wagtail-brow         right=True score=1.00 identical=True wrong-decision-rejected=True
whinchat-bield       right=True score=1.00 identical=True wrong-decision-rejected=True
woodruff-staithe     right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
