"""The answer key's rules for the Defra Staff Expense (Travel & Subsistence) Policy v2.0 (published August 2021),
as exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a
verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an answer
open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each unclear phrase
at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a new scenario cannot
fall silently into untested logic.

The duration hook. Lines 204-212 set the class of air travel by the length of the journey: "Air travel for journeys
of less than 5 hours should be via economy class only", "For journeys of between 5 hours and 10 hours a business
class flight may be purchased where" one of three listed cases holds, and "For journeys of over 10 hours a business
class flight may be purchased subject to approval from a manager or approver". "Less than" and "over" are strict.
A nonstop's journey is its scheduled minutes. The text does not say how a journey with a connection is measured:
the flights' minutes added together, or the elapsed time with the wait between flights. When both measures fall on
the same side of a limit the answer is clear; when they straddle it the rule returns None (unclear).

Two gaps the text leaves: exactly 5 hours is not "less than 5 hours", and whether "between 5 hours and 10 hours"
takes in its end points is not said (EDGE_CASES section 2: "between" is inclusive only if the handbook confirms it).
At exactly 300 minutes a traveller who meets one of the three cases may or may not have business class: unclear.
At exactly 600 minutes the journey is not "over 10 hours" on any reading, and business class is then only possible
through the three cases (inclusive reading) or not at all (exclusive reading): with none of the cases met, both
readings give economy; with one met, the readings differ and no scenario uses it.
"""

from contract import Approver, Cabin, Clause, Decision, Outcome, Purpose, ReasonCode, SignOffSubject

HANDBOOK = "Defra Staff Expense (Travel & Subsistence) Policy v2.0, published August 2021"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.INTRODUCTION: "Introduction",
    Clause.PURPOSE: "Purpose",
    Clause.OWNERSHIP: "Ownership",
    Clause.SCOPE: "Scope",
    Clause.PRINCIPLES: "Travel and subsistence principles",
    Clause.INDIVIDUAL_RESPONSIBILITIES: "Responsibility and liability - individuals' responsibilities",
    Clause.MANAGER_RESPONSIBILITIES: "Managers' responsibilities",
    Clause.SHARED_SERVICES_RESPONSIBILITIES: "SSCL responsibilities",
    Clause.SUSTAINABILITY: "Sustainability",
    Clause.TRAVEL_INITIATION: "Travel initiation and events",
    Clause.SOURCING: "Sourcing arrangements",
    Clause.RAIL_AND_AIR: "Rail and air travel, including class of travel",
    Clause.AIR: "Air",
    Clause.RAIL_CLASS: "Rail Class of travel",
    Clause.RAILCARDS: "Railcards",
    Clause.OYSTER_CARDS: "Oyster cards",
    Clause.MILEAGE: "Mileage claims",
    Clause.TAXIS: "Taxis",
    Clause.CAR_TRAVEL: "Additional provisions for travel by car",
    Clause.CAR_HIRE_ACCIDENTS: "Car hire accidents",
    Clause.SUBSISTENCE: "Subsistence",
    Clause.HOTEL_RATES: "Hotel rates",
    Clause.LODGING: "Lodging allowance",
    Clause.FOREIGN_TRAVEL: "Foreign travel",
    Clause.FRIENDS_AND_FAMILY: "Friends and family allowance",
    Clause.TIPS: "Tips and gratuities",
    Clause.ALCOHOL: "Alcohol",
    Clause.TELEPHONE: "Telephone calls",
    Clause.INCIDENTALS: "Other incidental expenses",
    Clause.AMENDMENTS: "Amendments to the policy",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both sides of
# each). "economy-only": a journey is over this rule's limit when it is NOT "less than 5 hours" (300 minutes or
# more, inclusive). "ten-hours": over when the journey is "over 10 hours" (more than 600 minutes, strict).
DURATION_RULES = (
    {"name": "economy-only", "minutes": 300, "operator": ">=", "lines": [204, 204],
     "quote": "Air travel for journeys of less than 5 hours should be via economy class only."},
    {"name": "ten-hours", "minutes": 600, "operator": ">", "lines": [211, 212],
     "quote": "For journeys of over 10 hours a business class flight may be purchased subject to approval from a "
              "manager or approver."},
)
LIMITS = {rule["name"]: (rule["minutes"], rule["operator"]) for rule in DURATION_RULES}
FIVE_HOURS = 300
TEN_HOURS = 600

# Handbook-specific conventions shown by booking_requirements, beyond the template's. The task instructions
# carry the same sentence, so no reader counts airport transfers into a journey (the world has none).
CONVENTIONS = ("No time is counted for getting to or from an airport: a nonstop flight's length is its scheduled minutes.",)

# Lines 180-181: air travel between locations on mainland England, Wales and Scotland. The shared world's airports
# there (Northern Ireland, the islands and Ireland are not mainland Great Britain).
MAINLAND_GB = ("LHR", "LGW", "EDI")

GAP_PHRASE = "For journeys of between 5 hours and 10 hours"
JOURNEY_PHRASE = "Air travel for journeys of less than 5 hours should be via economy class only."

# Who a hold over unclear words may name: nobody is named to settle the text; lines 86-88 send travel outside the
# policy to line management for prior approval, and line 195 needs a manager or approver for all air travel. Such
# a hold also waits on that sign-off, so APPROVAL_REQUIRED may stand beside UNCLEAR_POLICY_TEXT.
UNCLEAR_ROLES = [Approver.NOT_NAMED, Approver.MANAGER]
UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
AIR_CLAUSES = [Clause.RAIL_AND_AIR, Clause.AIR]
DECLINED = [ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET]


def measures(offer):
    """The journey's minutes on each reading: a nonstop's scheduled minutes; for a connection, the flights'
    minutes added together and the elapsed minutes with the time on the ground."""
    if offer.stops == 0:
        return [offer.flying_minutes]
    return [offer.flying_minutes, offer.elapsed_minutes]


def beyond(minutes, rule):
    limit, operator = LIMITS[rule]
    return minutes >= limit if operator == ">=" else minutes > limit


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s outbound journey is over the handbook's ``rule``
    (economy-only: not less than 300 minutes; ten-hours: more than 600 minutes), on every reading of how a
    journey with a connection is measured."""
    if rule not in LIMITS:
        raise ValueError(f"unknown duration rule {rule!r}")
    verdicts = {beyond(minutes, rule) for minutes in measures(offer)}
    if len(verdicts) == 2:
        return None
    return verdicts.pop()


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reasons, approvers, clauses, why):
    return answer(Decision.REFUSE, [], reasons, approvers, clauses, why)


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def in_cabin(offers, cabin):
    return [offer for offer in offers if offer.cabin == cabin]


def records(trip, subject, outcome, roles):
    return sorted({record.role for record in trip.sign_offs
                   if record.subject == subject and record.outcome == outcome and record.role in roles},
                  key=lambda role: role.value)


def on_file(trip, roles):
    """Approvers a booking accepts (SYNC_NOTES 4'): the roles whose sign-off it relies on, already given, and NONE
    (readers split on whether a sign-off already given is still relied on), plus any other role on file."""
    return [Approver.NONE, *roles, *(record.role for record in trip.sign_offs if record.outcome == Outcome.GIVEN)]


def lands_in_time(trip, offer):
    """Line 187, "the lowest practical fare": an offer that lands after the traveller's business begins is not
    practical. Both times are local at the destination, as YYYY-MM-DD HH:MM text."""
    return offer.segments[-1].arrive_local <= trip.business_starts


def practical(trip, offers):
    return [offer for offer in offers if lands_in_time(trip, offer)]


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted offer
    id, cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys a one-way ticket")
    seated = [offer for offer in offers if offer.seats_available]
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      on_file(trip, []), [Clause.INTRODUCTION, Clause.PURPOSE, Clause.PRINCIPLES, Clause.SCOPE],
                      "Lines 42-43: only expenses actually and necessarily incurred in the course of official business "
                      "are reimbursed; lines 69-71: the policy covers travel in the course of official business. A "
                      "personal trip is not official business, so the department buys no ticket.")
    exception = []
    if trip.origin.code in MAINLAND_GB and trip.destination.code in MAINLAND_GB:
        granted = records(trip, SignOffSubject.POLICY_EXCEPTION, Outcome.GIVEN, [Approver.DIRECTOR])
        refused = records(trip, SignOffSubject.POLICY_EXCEPTION, Outcome.REFUSED, [Approver.DIRECTOR])
        if refused and not granted:
            return refuse([ReasonCode.DOMESTIC_AIR_NOT_PERMITTED, ReasonCode.RAIL_PREFERRED,
                           ReasonCode.NO_COMPLIANT_OFFER],
                          on_file(trip, [Approver.DIRECTOR]), AIR_CLAUSES,
                          "Lines 180-181: air travel between locations on mainland England, Wales and Scotland is not "
                          "permitted unless approval by exception is granted by a director; the director refused the "
                          "exception, so no flight is bought (lines 182-184: rail is the preferred means).")
        if not granted:
            raise ValueError("a mainland flight without a director's answer is not modelled")
        exception = granted
    if trip.feels_unsafe:
        return safety(trip, seated)
    manager = records(trip, SignOffSubject.AIR_TRAVEL, Outcome.GIVEN, [Approver.MANAGER])
    if not manager:
        raise ValueError("a flight without the manager's prior approval of air travel is not modelled")
    if exception:
        if trip.requested_cabin != Cabin.ECONOMY:
            raise ValueError("a mainland flight outside economy is not modelled")
        lowest = cheapest(practical(trip, in_cabin(seated, Cabin.ECONOMY)))
        if not lowest or any(over("economy-only", offer) is not False for offer in lowest):
            raise ValueError("a mainland flight needs a short economy offer")
        return answer(Decision.BOOK, lowest, [ReasonCode.POLICY_EXCEPTION_APPROVED, ReasonCode.LOWEST_FARE],
                      on_file(trip, [*exception, *manager]), AIR_CLAUSES,
                      "Lines 180-181: the director granted the exception for air travel within mainland Great Britain; "
                      "line 195: the manager approved the air travel in advance; line 204: under 5 hours, economy only; "
                      "line 187: the lowest practical fare.")
    if trip.requested_cabin == Cabin.ECONOMY:
        return economy(trip, seated, manager)
    if trip.requested_cabin == Cabin.PREMIUM_ECONOMY:
        return premium(trip, seated, manager)
    if trip.requested_cabin == Cabin.BUSINESS:
        return business(trip, seated, manager, asked_first=False)
    if trip.requested_cabin == Cabin.FIRST:
        return business(trip, seated, manager, asked_first=True)
    raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")


def safety(trip, seated):
    """Lines 92-98: when a traveller feels unsafe and it is not practical to seek prior approval before taking
    additional steps, approval can be obtained retrospectively. The step here is the first flight out."""
    if trip.manager_reachable or trip.sign_offs or trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError("a safety case with an approver to hand, a sign-off on file or a premium cabin is not modelled")
    economy_offers = in_cabin(seated, Cabin.ECONOMY)
    if not economy_offers or any(over("economy-only", offer) is not False for offer in economy_offers):
        raise ValueError("a safety case needs short economy flights")
    first = min(offer.segments[0].depart_utc for offer in economy_offers)
    earliest = [offer for offer in economy_offers if offer.segments[0].depart_utc == first]
    return answer(Decision.BOOK, earliest, [ReasonCode.TRAVELLER_SAFETY], [Approver.NONE, Approver.MANAGER],
                  [Clause.PRINCIPLES, *AIR_CLAUSES],
                  "Lines 92-98: the traveller feels unsafe and the line manager cannot be reached, so prior approval "
                  "(line 195) is not practical and approval can be obtained retrospectively: book the first flight out, "
                  "in economy (line 204: under 5 hours).")


def economy(trip, seated, manager):
    """An economy request. Line 187: the lowest practical fare within the permitted class. Lines 205-208: when no
    lower-class seat can be booked and the timing or date cannot be changed, a 5-10 hour journey may be in
    business class."""
    economy_offers = practical(trip, in_cabin(seated, Cabin.ECONOMY))
    if economy_offers:
        lowest = cheapest(economy_offers)
        if any(offer.refundable for offer in lowest):
            raise ValueError("a refundable lowest fare is not modelled")
        listed = cheapest(in_cabin(seated, Cabin.ECONOMY))
        late = lowest != listed
        return answer(Decision.BOOK, lowest, [ReasonCode.LOWEST_FARE], on_file(trip, manager), AIR_CLAUSES,
                      "Line 187: the lowest practical fare within the permitted class of travel (economy, as asked); "
                      "line 195: the manager approved the air travel in advance."
                      + (" A cheaper fare lands after the business begins, so it is not practical." if late else ""))
    if in_cabin(seated, Cabin.PREMIUM_ECONOMY) or in_cabin(seated, Cabin.ECONOMY):
        raise ValueError("an economy request with only premium economy or late economy seats is not modelled")
    if not trip.date_fixed:
        raise ValueError("no economy seat on a date that may move is not modelled")
    business_offers = practical(trip, in_cabin(seated, Cabin.BUSINESS))
    bands = {band(offer) for offer in business_offers}
    if bands != {"between"}:
        raise ValueError("no economy seat outside a clear 5-10 hour journey is not modelled")
    return answer(Decision.BOOK, cheapest(business_offers), [ReasonCode.NO_ECONOMY_SEATS_URGENT],
                  on_file(trip, manager), AIR_CLAUSES,
                  "Lines 205-208: a journey of between 5 and 10 hours, no seat can be booked in the lower class and the "
                  "date cannot be changed, so a business class flight may be purchased: the cheapest (line 187).")


def premium(trip, seated, manager):
    """A premium economy request. Line 204: journeys of less than 5 hours are via economy class only."""
    economy_offers = practical(trip, in_cabin(seated, Cabin.ECONOMY))
    if not economy_offers or any(over("economy-only", offer) is not False for offer in seated):
        raise ValueError("a premium economy request on a journey of 5 hours or more is not modelled")
    return answer(Decision.BOOK, cheapest(economy_offers), DECLINED, on_file(trip, manager), AIR_CLAUSES,
                  "Line 204: the journey is under 5 hours, so air travel is via economy class only; premium economy "
                  "is declined. Line 187: the lowest practical economy fare. (Lines 221-222 permit Eurostar Standard "
                  "Premier on value for money; that is rail, not air.)")


def band(offer):
    """Which of lines 204-212 a journey falls in: 'under' (less than 5 hours), 'gap' (exactly 5 hours on a
    nonstop), 'between', 'ten' (exactly 10 hours), 'over' (over 10 hours), or 'unclear' (a connection measured
    two ways that straddle a limit)."""
    short, long = over("economy-only", offer), over("ten-hours", offer)
    if short is None or long is None:
        return "unclear"
    if short is False:
        return "under"
    if long is True:
        return "over"
    if FIVE_HOURS in measures(offer):
        if offer.stops:
            raise ValueError("a connection measured at exactly 5 hours is not modelled")
        return "gap"
    if TEN_HOURS in measures(offer):
        return "ten"
    return "between"


def cases_met(trip, seated):
    """Lines 205-210: the three cases in which a 5-10 hour journey may be in business class: no booking in the
    lower class with timing or date fixed, work immediately on arrival, disability or medical grounds."""
    reasons = []
    if not in_cabin(seated, Cabin.ECONOMY) and not in_cabin(seated, Cabin.PREMIUM_ECONOMY) and trip.date_fixed:
        reasons.append(ReasonCode.NO_ECONOMY_SEATS_URGENT)
    if trip.straight_to_work:
        reasons.append(ReasonCode.WORK_ON_ARRIVAL)
    if trip.health_letter_on_file:
        reasons.append(ReasonCode.MEDICAL_NEED)
    return reasons


def business(trip, seated, manager, asked_first):
    """A business (or first) request. Lines 196-203: first class is banned, except that overseas, where the
    airline's "first" is akin to business class and there is no genuine business class, it may be used under the
    business-class rules. Lines 204-212: the class by the length of the journey."""
    business_offers = practical(trip, in_cabin(seated, Cabin.BUSINESS))
    first_offers = practical(trip, in_cabin(seated, Cabin.FIRST))
    economy_offers = practical(trip, in_cabin(seated, Cabin.ECONOMY))
    if not economy_offers:
        raise ValueError("a premium request with no economy seat is not modelled")
    akin = False
    if not in_cabin(seated, Cabin.BUSINESS) and first_offers:
        if asked_first or not trip.first_is_business_grade or trip.origin.country == "GB":
            raise ValueError("first class without a business cabin is only modelled overseas, akin to business")
        business_offers, akin = first_offers, True
    if not business_offers:
        raise ValueError("a business request with no business-grade offer is not modelled")
    bands = {band(offer) for offer in [*business_offers, *economy_offers]}
    if len(bands) != 1:
        raise ValueError("offers in different duration bands are not modelled")
    where = bands.pop()
    cases = cases_met(trip, seated)
    lowest = cheapest(economy_offers)
    best = cheapest(business_offers)
    banned = [ReasonCode.FIRST_CLASS_BANNED] if asked_first else []
    if asked_first and trip.first_is_business_grade:
        raise ValueError("a first request where first is akin to business is not modelled")
    first_note = (" Lines 196-197: there is a complete ban on first class air travel, and this route has a genuine "
                  "business class (lines 202-203), so first is declined.") if asked_first else ""
    granted = [ReasonCode.FIRST_AKIN_TO_BUSINESS] if akin else []
    akin_note = (" Lines 196-202: overseas, the airline's 'first' is akin to business class and there is no genuine "
                 "business class, so it may be used under the business-class rules.") if akin else ""
    if where == "under":
        if trip.health_letter_on_file:
            raise ValueError("a medical need on a journey under 5 hours is not modelled")
        return answer(Decision.BOOK, lowest, [*banned, *DECLINED], on_file(trip, manager), AIR_CLAUSES,
                      "Line 204: the journey is under 5 hours, so air travel is via economy class only; the premium "
                      "cabin is declined. Line 187: the lowest practical fare." + first_note)
    if where == "gap":
        if not cases:
            raise ValueError("exactly 5 hours with none of the three cases is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, [*best, *lowest], UNCLEAR_REASONS, UNCLEAR_ROLES,
                      [*AIR_CLAUSES, Clause.PRINCIPLES],
                      "Lines 204-210: the journey is exactly 5 hours. It is not 'less than 5 hours', so economy is not "
                      "required by line 204, but the text does not say whether 'between 5 hours and 10 hours' includes "
                      "5 hours; if it does, the traveller's case allows business class, if not, no line allows it. "
                      "Hold the business fare (or the economy fare of the other reading).", phrase=GAP_PHRASE)
    if where == "unclear":
        if not cases:
            raise ValueError("an unclear journey with none of the three cases is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, [*best, *lowest], UNCLEAR_REASONS, UNCLEAR_ROLES,
                      [*AIR_CLAUSES, Clause.PRINCIPLES],
                      "Lines 204-210: the flights add up to less than 5 hours, but with the connection the journey takes "
                      "more than 5 hours. The text does not say how a journey is measured: by flying time it is economy "
                      "only (line 204); from first departure to last arrival the traveller's case allows business class (lines 205-209). "
                      "Hold the business fare (or the economy fare of the other reading).", phrase=JOURNEY_PHRASE)
    if where in ("between", "ten"):
        if where == "ten" and cases:
            raise ValueError("exactly 10 hours with one of the three cases is not modelled")
        if cases:
            # A first request is declined on the ban, so its reason names the ban, not the case that allows business.
            reasons = [*banned, ReasonCode.UPGRADE_NOT_ELIGIBLE] if asked_first else [*cases, *granted]
            return answer(Decision.BOOK, best, reasons, on_file(trip, manager), AIR_CLAUSES,
                          "Lines 205-210: a journey of between 5 and 10 hours, and one of the listed cases holds, so a "
                          "business class flight may be purchased: the cheapest (line 187); line 195: the manager "
                          "approved the air travel." + first_note + akin_note)
        business_signed = records(trip, SignOffSubject.BUSINESS_CLASS, Outcome.GIVEN, [Approver.MANAGER])
        return answer(Decision.BOOK, lowest, [*banned, *DECLINED], on_file(trip, business_signed + manager),
                      AIR_CLAUSES,
                      "Lines 205-212: the journey is not over 10 hours, and none of the cases that allow business class "
                      "between 5 and 10 hours holds (the traveller's business does not start on arrival, an economy "
                      "seat is free, no medical grounds), so economy; line 187: the lowest practical fare. A manager's "
                      "yes to business class 'if the policy allows it' does not change that." + first_note)
    # where == "over": lines 211-212, business class subject to approval from a manager or approver.
    if asked_first or akin:
        raise ValueError("first class on a journey over 10 hours is not modelled")
    signed = records(trip, SignOffSubject.BUSINESS_CLASS, Outcome.GIVEN, [Approver.MANAGER])
    awaited = records(trip, SignOffSubject.BUSINESS_CLASS, Outcome.AWAITED, [Approver.MANAGER])
    if signed:
        return answer(Decision.BOOK, best, [ReasonCode.LONG_FLIGHT_APPROVED, ReasonCode.INTERNATIONAL_LONG_FLIGHT],
                      on_file(trip, signed + manager), AIR_CLAUSES,
                      "Lines 211-212: the journey is over 10 hours, so a business class flight may be purchased subject "
                      "to approval from a manager or approver, and the manager approved it: the cheapest business fare.")
    if awaited:
        return answer(Decision.FLAG_FOR_APPROVAL, best,
                      [ReasonCode.APPROVAL_REQUIRED, ReasonCode.INTERNATIONAL_LONG_FLIGHT], awaited, AIR_CLAUSES,
                      "Lines 211-212: the journey is over 10 hours, so business class may be purchased subject to "
                      "approval from a manager or approver; the manager has not answered yet, so hold the cheapest "
                      "business fare for that approval.")
    raise ValueError("business over 10 hours with no approval asked is not modelled")
