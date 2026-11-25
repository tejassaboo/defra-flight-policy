"""Writes the Defra scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Expected answers are hand-written here; tests/test_scenarios.py checks them against rules.solve. Fares are in pence
(handbook.json currency GBP).
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on (frozen line numbers; quotes keep the text as it is, footers included) -----
OFFICIAL = keep(40, 43, None, "only expenses actually and necessarily incurred in the course of official business")
PURPOSE = keep(69, 71, None, "the policy covers travel in the course of official business")
OUTSIDE = keep(86, 91, None, "travel outside the policy needs line management's prior approval")
SAFETY = keep(92, 98, None, "a traveller who feels unsafe may take further steps and get approval afterwards")
MAINLAND = keep(180, 181, None, "no air travel within mainland England, Wales and Scotland without a director's exception")
RAIL = keep(182, 184, None, "rail is the preferred means where travel is unavoidable")
LOWEST = keep(187, 187, None, "the lowest practical fare within the permitted class")
PRIOR = keep(195, 195, None, "all air travel needs a manager's or approver's prior approval")
FIRST = keep(196, 203, None, "first class is banned, except an overseas 'first' akin to business where there is no "
             "genuine business class")
UNDER = keep(204, 204, None, "under 5 hours: economy only")
BETWEEN = keep(205, 210, None, "5 to 10 hours: business in three listed cases")
OVER = keep(211, 212, None, "over 10 hours: business with a manager's or approver's approval")

# ----- nearby clauses that must not change the answer -----
EUROSTAR = aside(220, 222, "Eurostar Standard Premier is permitted where good value for money can be demonstrated.",
                 "a rail rule on value for money, not a cabin rule for flights")

# ----- builders -----

def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "origin": "", "destination": "", "travel_date": "",
        "booking_date": "", "business_starts": "", "purpose": "", "purpose_kind": "MEETING",
        "requested_cabin": "ECONOMY", "straight_to_work": False, "date_fixed": True, "health_letter_on_file": False,
        "first_is_business_grade": False, "feels_unsafe": False, "manager_reachable": True, "sign_offs": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def sign(role, name, subject, outcome="GIVEN", note=""):
    return {"role": role, "name": name, "subject": subject, "outcome": outcome, "note": note}


def air(name, note):
    return sign("MANAGER", name, "AIR_TRAVEL", "GIVEN", note)


def offer(slot, flight, cabin, pence, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": pence}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": reasons,
            "approvers": approvers, "clauses": clauses, "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=0):
    # handbook.json background_offers is 0, and no search here adds any: a search the scenario does not pin lists
    # nothing, and the pinned ones list exactly these offers.
    return {"name": "main", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


S = []


def scenario(id, category, overlays, request, trip_, search_spec, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": [search_spec]}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


AIR = ["AIR", "RAIL_AND_AIR"]
ON_FILE = ["MANAGER", "NONE"]
DECLINED = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
UNCLEAR_ROLES = ["MANAGER", "NOT_NAMED"]
UNCLEAR_REASONS = ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"]
UNCLEAR_CLAUSES = ["AIR", "PRINCIPLES", "RAIL_AND_AIR"]

# ===== easy (5) =====

scenario(
    "bracken-stile", "easy", [],
    "I need to get from Heathrow to Frankfurt on 8 December for the EU plant health working group, which starts at "
    "15:00. Economy, the cheapest seat please.",
    trip(traveller_name="Rachel Okafor", traveller_title="Senior Policy Adviser, Plant Health", origin="LHR",
         destination="FRA", travel_date="2026-12-08", booking_date="2026-11-24", business_starts="2026-12-08 15:00",
         purpose="EU plant health working group in Frankfurt",
         sign_offs=[air("Helen Ashworth", "Approved: fly to Frankfurt for the working group.")]),
    search("LHR", "FRA", "2026-12-08", {
        "early": {"carrier": "LH", "depart": "07:00"},
        "mid": {"carrier": "BA", "depart": "09:30"},
        "noon": {"carrier": "LH", "depart": "12:10"},
    }, [
        offer("early-economy", "early", "ECONOMY", 9800, seats=False),
        offer("mid-economy", "mid", "ECONOMY", 11200),
        offer("mid-business", "mid", "BUSINESS", 38500),
        offer("noon-economy", "noon", "ECONOMY", 12900),
    ]),
    expected("BOOK", ["mid-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, UNDER, PRIOR],
    "A 75-minute flight: under 5 hours, economy only (line 204), at the lowest practical fare (line 187). The 07:00 "
    "fare is cheaper but sold out. The manager's prior approval of the air travel is on file (line 195).")

scenario(
    "curlew-hithe", "easy", ["upgrade_not_taken"],
    "Please book me Heathrow to Singapore on 12 January for the ASEAN wildlife trade talks, which start on the 14th. "
    "Economy is fine, the cheapest one.",
    trip(traveller_name="Tom Hargreaves", traveller_title="International Wildlife Trade Lead", origin="LHR",
         destination="SIN", travel_date="2027-01-12", booking_date="2026-12-01", business_starts="2027-01-14 09:00",
         purpose="ASEAN wildlife trade talks in Singapore", purpose_kind="NEGOTIATION",
         sign_offs=[air("Gareth Pryce", "Approved: fly to Singapore for the ASEAN talks.")]),
    search("LHR", "SIN", "2027-01-12", {
        "british": {"carrier": "BA", "depart": "11:05", "minutes": [790]},
        "singapore": {"carrier": "SQ", "depart": "20:40", "minutes": [780]},
    }, [
        offer("british-economy", "british", "ECONOMY", 61200),
        offer("british-business", "british", "BUSINESS", 389000),
        offer("singapore-economy", "singapore", "ECONOMY", 64800),
        offer("singapore-business", "singapore", "BUSINESS", 402000),
    ]),
    expected("BOOK", ["british-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, OVER, PRIOR],
    "A journey of over 10 hours could be in business class with approval (lines 211-212), but the traveller asks for "
    "the cheapest economy seat: the lowest practical fare (line 187). Both flights land before the talks.")

scenario(
    "dipper-combe", "easy", ["dearer_option"],
    "Heathrow to New York JFK on 2 February for the UN oceans preparatory meeting, which starts the next morning. "
    "Occupational health has a letter on file about my back, so I need a business-class seat if the policy allows it; "
    "otherwise economy.",
    trip(traveller_name="Priya Natarajan", traveller_title="Marine Policy Manager", origin="LHR", destination="JFK",
         travel_date="2027-02-02", booking_date="2027-01-05", business_starts="2027-02-03 09:00",
         purpose="UN oceans preparatory meeting in New York", requested_cabin="BUSINESS", health_letter_on_file=True,
         sign_offs=[air("Gareth Pryce", "Approved: fly to New York for the oceans meeting.")]),
    search("LHR", "JFK", "2027-02-02", {
        "british": {"carrier": "BA", "depart": "10:15", "minutes": [460]},
        "virgin": {"carrier": "VS", "depart": "11:40", "minutes": [465]},
    }, [
        offer("british-economy", "british", "ECONOMY", 52400),
        offer("british-business", "british", "BUSINESS", 248000),
        offer("virgin-economy", "virgin", "ECONOMY", 49800),
        offer("virgin-business", "virgin", "BUSINESS", 236000),
    ]),
    expected("BOOK", ["virgin-business"], ["BUSINESS"], ["MEDICAL_NEED"], ON_FILE, AIR),
    [BETWEEN, LOWEST, PRIOR],
    "460 and 465 minutes: between 5 and 10 hours. A business class flight may be purchased on disability/medical "
    "grounds (lines 205, 210), and the occupational health letter is on file: the cheapest business fare (line 187).")

scenario(
    "foxglove-shingle", "easy", ["multi_leg", "upgrade_not_taken"],
    "Heathrow to Bogota on 9 March for the Andean paramo restoration workshop, which opens on the 11th. Economy, the "
    "cheapest please; a connection is fine.",
    trip(traveller_name="Owen Llewellyn", traveller_title="Peatland Restoration Specialist", origin="LHR",
         destination="BOG", travel_date="2027-03-09", booking_date="2027-02-08", business_starts="2027-03-11 09:00",
         purpose="Andean paramo restoration workshop in Bogota", purpose_kind="CONFERENCE",
         sign_offs=[air("Gareth Pryce", "Approved: fly to Bogota for the workshop.")]),
    search("LHR", "BOG", "2027-03-09", {
        "madrid": {"carrier": "IB", "via": ["MAD"], "depart": "07:15", "layovers": [95]},
        "avianca": {"carrier": "AV", "depart": "13:30"},
        "british": {"carrier": "BA", "depart": "14:10"},
    }, [
        offer("madrid-economy", "madrid", "ECONOMY", 58700),
        offer("madrid-business", "madrid", "BUSINESS", 312000),
        offer("avianca-economy", "avianca", "ECONOMY", 66300),
        offer("avianca-business", "avianca", "BUSINESS", 345000),
        offer("british-economy", "british", "ECONOMY", 71900),
    ]),
    expected("BOOK", ["madrid-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, PRIOR],
    "Economy asked, connections welcome: the Iberia connection through Madrid is the lowest practical fare (line 187) "
    "and lands well before the workshop. Business class over 10 hours (lines 211-212) is not asked for.")

scenario(
    "gentian-sike", "easy", ["multi_leg", "date_arithmetic"],
    "Edinburgh to Paris CDG on 15 December; the OECD environment policy committee meets the next morning at 09:30. "
    "Cheapest economy, I don't mind changing planes.",
    trip(traveller_name="Fiona MacLeod", traveller_title="Environment Economist", origin="EDI", destination="CDG",
         travel_date="2026-12-15", booking_date="2026-11-26", business_starts="2026-12-16 09:30",
         purpose="OECD environment policy committee in Paris",
         sign_offs=[air("Helen Ashworth", "Approved: fly to Paris for the OECD committee.")]),
    search("EDI", "CDG", "2026-12-15", {
        "airfrance": {"carrier": "AF", "depart": "08:10"},
        "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "15:20", "layovers": [70]},
    }, [
        offer("airfrance-economy", "airfrance", "ECONOMY", 18900),
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 14300),
    ]),
    expected("BOOK", ["amsterdam-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, UNDER, PRIOR],
    "Edinburgh to Paris is not within mainland Great Britain. The KLM connection lands at 19:50 Paris time on the 15th, "
    "the evening before the 09:30 meeting on the 16th, so it is practical and the lowest fare (line 187); under 5 hours "
    "on every measure, economy (line 204).",
    distractors=[aside(180, 181, "Air travel between locations on mainland England, Wales and Scotland is not",
                       "Edinburgh to Paris leaves Great Britain")])

# ===== boundary twins (6) =====

CAIRO_REQUEST = ("Heathrow to Cairo on 20 January. I go straight from the airport into the Nile water-sharing talks at "
                 "the ministry, so I'd like business class if the policy allows it; otherwise economy is fine.")


def cairo(id, category, minutes, exp, notes, twin_of="", twin_fact="", flag_twins=(), ambiguity="none",
          name="Daniel Mensah", overlays=()):
    scenario(
        id, category, list(overlays), CAIRO_REQUEST,
        trip(traveller_name=name, traveller_title="Water Security Adviser", origin="LHR", destination="CAI",
             travel_date="2027-01-20", booking_date="2026-12-14", business_starts="2027-01-20 16:30",
             purpose="Nile water-sharing talks at the Egyptian water ministry", purpose_kind="NEGOTIATION",
             requested_cabin="BUSINESS", straight_to_work=True,
             sign_offs=[air("Gareth Pryce", "Approved: fly to Cairo for the water talks.")]),
        search("LHR", "CAI", "2027-01-20", {
            "british": {"carrier": "BA", "depart": "07:35", "minutes": [minutes]},
            "egyptair": {"carrier": "MS", "depart": "08:40", "minutes": [minutes]},
        }, [
            offer("british-economy", "british", "ECONOMY", 31800),
            offer("british-business", "british", "BUSINESS", 142000),
            offer("egyptair-economy", "egyptair", "ECONOMY", 28900),
            offer("egyptair-business", "egyptair", "BUSINESS", 131500),
        ]),
        exp, [UNDER, BETWEEN, LOWEST, PRIOR], notes, twin_of=twin_of, twin_fact=twin_fact, flag_twins=flag_twins,
        ambiguity=ambiguity)


cairo("hawthorn-ings", "boundary_twin", 299,
      expected("BOOK", ["egyptair-economy"], ["ECONOMY"], DECLINED, ON_FILE, AIR),
      "299-minute nonstops: 'less than 5 hours' (strict), so economy class only (line 204), even though the traveller "
      "works on arrival. Business is declined; the lowest practical fare (line 187).",
      twin_of="hornbeam-sett", twin_fact="scheduled minutes 299 or 301")

cairo("hornbeam-sett", "boundary_twin", 301,
      expected("BOOK", ["egyptair-business"], ["BUSINESS"], ["WORK_ON_ARRIVAL"], ON_FILE, AIR),
      "301-minute nonstops: between 5 and 10 hours, and the traveller goes straight into the talks, so 'staff will be "
      "required to work immediately on arrival' (line 209): business class may be purchased, the cheapest (line 187).",
      twin_of="hawthorn-ings", twin_fact="scheduled minutes 299 or 301", name="Daniel Mensah",
      overlays=["dearer_option"])

BEIJING_REQUEST = ("Heathrow to Beijing on 23 February for the UK-China soil science dialogue, which starts on the 25th. "
                   "My line manager has said yes to business class if the policy allows it; if it doesn't, economy.")


def beijing(id, minutes, exp, notes, overlays=()):
    scenario(
        id, "boundary_twin", list(overlays), BEIJING_REQUEST,
        trip(traveller_name="Alison Whitfield", traveller_title="Chief Soil Scientist", origin="LHR", destination="PEK",
             travel_date="2027-02-23", booking_date="2027-01-25", business_starts="2027-02-25 09:00",
             purpose="UK-China soil science dialogue in Beijing", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
             sign_offs=[air("Gareth Pryce", "Approved: fly to Beijing for the soil dialogue."),
                        sign("MANAGER", "Gareth Pryce", "BUSINESS_CLASS", "GIVEN",
                             "Yes to business class if the policy allows it on this flight.")]),
        search("LHR", "PEK", "2027-02-23", {
            "airchina": {"carrier": "CA", "depart": "12:00", "minutes": [minutes]},
            "british": {"carrier": "BA", "depart": "13:30", "minutes": [minutes]},
        }, [
            offer("airchina-economy", "airchina", "ECONOMY", 54600),
            offer("airchina-business", "airchina", "BUSINESS", 298000),
            offer("british-economy", "british", "ECONOMY", 59900),
            offer("british-business", "british", "BUSINESS", 315000),
        ]),
        exp, [OVER, BETWEEN, LOWEST, PRIOR], notes,
        twin_of="merlin-garth" if id == "kingcup-beck" else "kingcup-beck", twin_fact="scheduled minutes 600 or 601")


beijing("kingcup-beck", 600,
        expected("BOOK", ["airchina-economy"], ["ECONOMY"], DECLINED, ON_FILE, AIR),
        "600-minute nonstops are not 'over 10 hours' (strict, lines 211-212). Between 5 and 10 hours business needs one "
        "of the three cases of lines 205-210, and none holds (the dialogue starts two days later, economy seats are "
        "free, no medical grounds); read 'between' as exclusive and no line allows business either. Economy at the "
        "lowest practical fare (line 187); the manager's yes was only 'if the policy allows it'.")

beijing("merlin-garth", 601,
        expected("BOOK", ["airchina-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED"],
                 ON_FILE, AIR),
        "601-minute nonstops: over 10 hours, so a business class flight may be purchased subject to approval from a "
        "manager or approver (lines 211-212); the manager approved it. The cheapest business fare (line 187).",
        overlays=["dearer_option"])

DUBAI_FLIGHTS = {
    "emirates": {"carrier": "EK", "depart": "07:45", "minutes": [425]},
    "british": {"carrier": "BA", "depart": "09:20", "minutes": [425]},
}
DUBAI_OFFERS = [
    offer("emirates-economy", "emirates", "ECONOMY", 41200),
    offer("emirates-business", "emirates", "BUSINESS", 198000),
    offer("british-economy", "british", "ECONOMY", 44900),
    offer("british-business", "british", "BUSINESS", 211000),
]


def dubai(id, straight, starts, when, exp, notes, overlays=()):
    scenario(
        id, "boundary_twin", list(overlays),
        f"Heathrow to Dubai on 2 March for the climate finance negotiations. {when} Business class please if the policy "
        "allows it; otherwise economy.",
        trip(traveller_name="Samir Choudhury", traveller_title="Climate Finance Negotiator", origin="LHR",
             destination="DXB", travel_date="2027-03-02", booking_date="2027-02-01", business_starts=starts,
             purpose="Climate finance negotiations in Dubai", purpose_kind="NEGOTIATION", requested_cabin="BUSINESS",
             straight_to_work=straight,
             sign_offs=[air("Gareth Pryce", "Approved: fly to Dubai for the negotiations.")]),
        search("LHR", "DXB", "2027-03-02", DUBAI_FLIGHTS, DUBAI_OFFERS),
        exp, [BETWEEN, LOWEST, PRIOR], notes,
        twin_of="ouzel-scarp" if id == "nightjar-holm" else "nightjar-holm",
        twin_fact="the session starts on landing (21:30 that evening, straight from the airport) or the next morning")


dubai("nightjar-holm", True, "2027-03-02 21:30",
      "The evening session starts at 21:30 and I'm going there straight from the airport.",
      expected("BOOK", ["emirates-business"], ["BUSINESS"], ["WORK_ON_ARRIVAL"], ON_FILE, AIR),
      "425-minute nonstops: between 5 and 10 hours. The traveller goes from the airport straight into the session, so "
      "'staff will be required to work immediately on arrival' (line 209): the cheapest business fare (line 187).",
      overlays=["dearer_option"])

dubai("ouzel-scarp", False, "2027-03-03 09:00",
      "The first session is at 09:00 the morning after I land.",
      expected("BOOK", ["emirates-economy"], ["ECONOMY"], DECLINED, ON_FILE, AIR),
      "425-minute nonstops: between 5 and 10 hours, but none of the three cases of lines 205-210 holds (the work starts "
      "the next morning, economy seats are free, no medical grounds): economy at the lowest practical fare (line 187).")

# ===== multi-rule (4) =====

EDINBURGH_FLIGHTS = {
    "early": {"carrier": "BA", "depart": "07:10"},
    "mid": {"carrier": "BA", "depart": "09:40"},
    "late": {"carrier": "BA", "depart": "13:00"},
}
EDINBURGH_OFFERS = [
    offer("early-economy", "early", "ECONOMY", 9400),
    offer("mid-economy", "mid", "ECONOMY", 7800),
    offer("late-economy", "late", "ECONOMY", 10600),
]


def edinburgh(id, category, outcome, note, sentence, exp, notes, overlays=()):
    scenario(
        id, category, list(overlays),
        "Heathrow to Edinburgh on 10 December for the Scottish Government fisheries meeting at 14:00. " + sentence,
        trip(traveller_name="Callum Fraser", traveller_title="Fisheries Policy Manager", origin="LHR", destination="EDI",
             travel_date="2026-12-10", booking_date="2026-11-27", business_starts="2026-12-10 14:00",
             purpose="Scottish Government fisheries meeting in Edinburgh",
             sign_offs=[sign("DIRECTOR", "Margaret Doyle", "POLICY_EXCEPTION", outcome, note),
                        air("Helen Ashworth", "Approved: fly to Edinburgh for the fisheries meeting.")]),
        search("LHR", "EDI", "2026-12-10", EDINBURGH_FLIGHTS, EDINBURGH_OFFERS),
        exp, [MAINLAND, RAIL, LOWEST, PRIOR], notes,
        twin_of="wagtail-brow" if id == "pipit-moss" else "pipit-moss",
        twin_fact="the director's answer to the exception: GIVEN or REFUSED")


edinburgh("pipit-moss", "multi_rule", "GIVEN",
          "Exception granted to fly: the rail line north is closed for engineering works that week.",
          "My director has signed off an exception for me to fly because the rail line is closed that week. Cheapest "
          "economy please.",
          expected("BOOK", ["mid-economy"], ["ECONOMY"], ["LOWEST_FARE", "POLICY_EXCEPTION_APPROVED"],
                   ["DIRECTOR", "MANAGER", "NONE"], AIR),
          "London to Edinburgh is air travel within mainland Great Britain, permitted only with a director's exception "
          "(lines 180-181), which is on file, beside the manager's prior approval of the air travel (line 195). Economy "
          "only under 5 hours (line 204), at the lowest practical fare (line 187): the 09:40.")

edinburgh("wagtail-brow", "refusal", "REFUSED", "Please take the train; no exception for this trip.",
          "I asked my director for an exception to fly; she said no, but please book whatever you can.",
          expected("REFUSE", [], ["NONE"], ["DOMESTIC_AIR_NOT_PERMITTED", "NO_COMPLIANT_OFFER", "RAIL_PREFERRED"],
                   ["DIRECTOR", "MANAGER", "NONE"], AIR),
          "London to Edinburgh is air travel within mainland Great Britain, which 'is not permitted unless approval by "
          "exception is granted by a director' (lines 180-181). The director refused, so no flight is bought, whatever "
          "the fare; rail is the preferred means (lines 182-184). The manager's approval of air travel does not replace "
          "the director's exception.")

scenario(
    "quillwort-ness", "multi_rule", ["dearer_option"],
    "Heathrow to Doha on 26 January. I go from the plane straight to the ministerial working dinner at 20:00 where the "
    "food security agreement is negotiated. I'd like first class; if that isn't allowed, book what the policy allows. "
    "I have to be at the dinner.",
    trip(traveller_name="Eleanor Rhys", traveller_title="Lead Negotiator, Food Security", origin="LHR",
         destination="DOH", travel_date="2027-01-26", booking_date="2026-12-29", business_starts="2027-01-26 20:00",
         purpose="Food security agreement talks in Doha", purpose_kind="NEGOTIATION", requested_cabin="FIRST",
         straight_to_work=True,
         sign_offs=[air("Gareth Pryce", "Approved: fly to Doha for the food security talks.")]),
    search("LHR", "DOH", "2027-01-26", {
        "qatar": {"carrier": "QR", "depart": "08:00", "minutes": [405]},
        "british": {"carrier": "BA", "depart": "09:15", "minutes": [405]},
    }, [
        offer("qatar-economy", "qatar", "ECONOMY", 39800),
        offer("qatar-business", "qatar", "BUSINESS", 189000),
        offer("qatar-first", "qatar", "FIRST", 342000),
        offer("british-economy", "british", "ECONOMY", 43600),
        offer("british-business", "british", "BUSINESS", 205000),
        offer("british-first", "british", "FIRST", 368000),
    ]),
    expected("BOOK", ["qatar-business"], ["BUSINESS"], ["FIRST_CLASS_BANNED", "UPGRADE_NOT_ELIGIBLE"], ON_FILE, AIR),
    [FIRST, BETWEEN, LOWEST, PRIOR],
    "Lines 196-197: a complete ban on first class air travel; the exception for an airline 'first' akin to business "
    "does not apply where there is a genuine business class as well (lines 202-203), and both airlines sell one. The "
    "405-minute flight is between 5 and 10 hours and the traveller works on arrival (line 209), so business class: "
    "the cheapest (line 187).")

scenario(
    "ragwort-lea", "multi_rule", ["dearer_option"],
    "Heathrow to Mumbai on 16 February for the G20 environment ministers' summit, which opens the next morning. The "
    "summit date can't move and I can't travel on any other day. Economy please, but if economy is gone, book what the policy "
    "allows.",
    trip(traveller_name="Neil Ramsay", traveller_title="G20 Environment Sherpa", origin="LHR", destination="BOM",
         travel_date="2027-02-16", booking_date="2027-02-12", business_starts="2027-02-17 10:00",
         purpose="G20 environment ministers' summit in Mumbai", purpose_kind="CONFERENCE", date_fixed=True,
         sign_offs=[air("Gareth Pryce", "Approved: fly to Mumbai for the G20 summit.")]),
    search("LHR", "BOM", "2027-02-16", {
        "airindia": {"carrier": "AI", "depart": "09:00", "minutes": [545]},
        "british": {"carrier": "BA", "depart": "11:20", "minutes": [545]},
    }, [
        offer("airindia-economy", "airindia", "ECONOMY", 47800, seats=False),
        offer("airindia-business", "airindia", "BUSINESS", 221000),
        offer("british-economy", "british", "ECONOMY", 51200, seats=False),
        offer("british-premium", "british", "PREMIUM_ECONOMY", 98000, seats=False),
        offer("british-business", "british", "BUSINESS", 236000),
    ]),
    expected("BOOK", ["airindia-business"], ["BUSINESS"], ["NO_ECONOMY_SEATS_URGENT"], ON_FILE, AIR),
    [BETWEEN, LOWEST, PRIOR],
    "545-minute nonstops: between 5 and 10 hours. Every economy and premium economy seat is sold out and the summit "
    "fixes the date, so 'bookings are not available in the lower class and the timing or date of the journey cannot be "
    "changed' (lines 207-208): business class may be purchased, the cheapest (line 187).")

scenario(
    "samphire-dyke", "multi_rule", ["multi_leg", "date_arithmetic", "month_end", "dearer_option"],
    "Heathrow to Singapore on 30 November: I need to be at the opening session of the wildlife trade enforcement "
    "conference at 14:00 on 1 December. Cheapest economy that gets me there in time, please.",
    trip(traveller_name="Grace Adeyemi", traveller_title="Wildlife Crime Enforcement Lead", origin="LHR",
         destination="SIN", travel_date="2026-11-30", booking_date="2026-11-24", business_starts="2026-12-01 14:00",
         purpose="Wildlife trade enforcement conference in Singapore", purpose_kind="CONFERENCE",
         sign_offs=[air("Gareth Pryce", "Approved: fly to Singapore for the enforcement conference.")]),
    search("LHR", "SIN", "2026-11-30", {
        "british": {"carrier": "BA", "depart": "11:05", "minutes": [790]},
        "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "14:30", "minutes": [425, 450], "layovers": [140]},
        "singapore": {"carrier": "SQ", "depart": "20:40", "minutes": [780]},
    }, [
        offer("british-economy", "british", "ECONOMY", 61500),
        offer("british-business", "british", "BUSINESS", 391000),
        offer("dubai-economy", "dubai", "ECONOMY", 52800),
        offer("singapore-economy", "singapore", "ECONOMY", 58900),
        offer("singapore-business", "singapore", "BUSINESS", 405000),
    ]),
    expected("BOOK", ["british-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, PRIOR],
    "Line 187: the lowest practical fare. The Emirates connection lands at 15:25 on 1 December (Singapore time) and the "
    "Singapore Airlines nonstop at 17:40, both after the 14:00 opening, so neither is practical; the BA nonstop lands at "
    "08:15 on 1 December. The flight crosses from 30 November into 1 December.")

# ===== hidden clause (2) =====

scenario(
    "sedum-howe", "hidden_clause", ["dearer_option"],
    "I'm in New York this week and fly JFK to Los Angeles on 16 March, going straight from the airport into the "
    "California Air Resources Board meeting. Business class if the policy allows it: on this route the airlines sell "
    "only economy and what they call first, which the booking agent says is the same seat as business class elsewhere. "
    "If it isn't allowed, economy.",
    trip(traveller_name="Hannah Brooks", traveller_title="Air Quality Policy Adviser", origin="JFK", destination="LAX",
         travel_date="2027-03-16", booking_date="2027-02-22", business_starts="2027-03-16 15:30",
         purpose="California Air Resources Board meeting in Los Angeles, on a US visit", requested_cabin="BUSINESS",
         straight_to_work=True, first_is_business_grade=True,
         sign_offs=[air("Helen Ashworth", "Approved: the US visit's flights, including New York to Los Angeles.")]),
    search("JFK", "LAX", "2027-03-16", {
        "american": {"carrier": "AA", "depart": "08:00", "minutes": [370]},
        "delta": {"carrier": "DL", "depart": "09:30", "minutes": [375]},
    }, [
        offer("american-economy", "american", "ECONOMY", 31200),
        offer("american-first", "american", "FIRST", 118000),
        offer("delta-economy", "delta", "ECONOMY", 29800),
        offer("delta-first", "delta", "FIRST", 124000),
    ]),
    expected("BOOK", ["american-first"], ["FIRST"], ["FIRST_AKIN_TO_BUSINESS", "WORK_ON_ARRIVAL"], ON_FILE, AIR),
    [FIRST, BETWEEN, LOWEST, PRIOR],
    "Lines 196-203: first class is banned, but overseas, where the higher class an airline calls 'first' is akin to "
    "business class and there is no genuine business class (most likely on overseas internal flights), it may be used "
    "under the business-class rules. 370 and 375 minutes are between 5 and 10 hours and the traveller works on arrival "
    "(line 209), so the business-grade cabin may be bought: the cheapest, American's first (line 187).")

scenario(
    "teasel-croft", "hidden_clause", ["outside_air_section", "dearer_option"],
    "There were violent protests outside my hotel last night and I don't feel safe here. Please get me on the first "
    "flight back to Heathrow today; it's 06:30 here now. My manager is on leave and I can't reach anyone to approve "
    "it.",
    trip(traveller_name="Joseph Kariuki", traveller_title="Fisheries Science Adviser", origin="IST", destination="LHR",
         travel_date="2026-12-04", booking_date="2026-12-04", business_starts="2026-12-07 09:00",
         purpose="Return to London from the Black Sea fisheries meeting in Istanbul", purpose_kind="RETURN_FROM_DUTY",
         feels_unsafe=True, manager_reachable=False, date_fixed=False),
    search("IST", "LHR", "2026-12-04", {
        "turkish-early": {"carrier": "TK", "depart": "09:10", "minutes": [235]},
        "british": {"carrier": "BA", "depart": "13:45", "minutes": [240]},
        "turkish-late": {"carrier": "TK", "depart": "18:30", "minutes": [235]},
    }, [
        offer("turkish-early-economy", "turkish-early", "ECONOMY", 32500),
        offer("british-economy", "british", "ECONOMY", 27400),
        offer("turkish-late-economy", "turkish-late", "ECONOMY", 21800),
    ]),
    expected("BOOK", ["turkish-early-economy"], ["ECONOMY"], ["TRAVELLER_SAFETY"], ON_FILE,
             ["AIR", "PRINCIPLES", "RAIL_AND_AIR"]),
    [SAFETY, PRIOR, UNDER],
    "Line 195 needs prior approval for all air travel, but lines 92-98: where employees feel unsafe and it is not "
    "practical to seek prior approval before taking additional steps, approval can be obtained retrospectively. The "
    "traveller feels unsafe and no approver can be reached: book the first flight out (09:10), in economy (line 204), "
    "though later flights are cheaper.")

# ===== distractor (2) =====

scenario(
    "thrift-gill", "distractor", [],
    "Heathrow to Dublin on 14 January for the all-island animal health meeting at 13:00. Cheapest economy, please.",
    trip(traveller_name="Siobhan Kelly", traveller_title="Animal Health Policy Officer", origin="LHR", destination="DUB",
         travel_date="2027-01-14", booking_date="2026-12-17", business_starts="2027-01-14 13:00",
         purpose="All-island animal health meeting in Dublin",
         sign_offs=[air("Helen Ashworth", "Approved: fly to Dublin for the animal health meeting.")]),
    search("LHR", "DUB", "2027-01-14", {
        "aerlingus-early": {"carrier": "EI", "depart": "07:20"},
        "british": {"carrier": "BA", "depart": "08:35"},
        "aerlingus-late": {"carrier": "EI", "depart": "10:50"},
    }, [
        offer("aerlingus-early-economy", "aerlingus-early", "ECONOMY", 8600),
        offer("british-economy", "british", "ECONOMY", 9900),
        offer("aerlingus-late-economy", "aerlingus-late", "ECONOMY", 7400),
    ]),
    expected("BOOK", ["aerlingus-late-economy"], ["ECONOMY"], ["LOWEST_FARE"], ON_FILE, AIR),
    [LOWEST, UNDER, PRIOR],
    "Dublin is not on mainland England, Wales or Scotland, so the ban of lines 180-181 does not apply. Under 5 hours, "
    "economy (line 204); the 10:50 lands at 11:50, before the 13:00 meeting: the lowest practical fare (line 187).",
    distractors=[aside(180, 181, "Air travel between locations on mainland England, Wales and Scotland is not",
                       "the ban covers flights within mainland Great Britain, not to Ireland"),
                 aside(182, 184, "Where travel is unavoidable rail is the preferred means",
                       "a preference, not a ban; there is no rail line to Dublin")])

scenario(
    "vervain-knowe", "distractor", [],
    "Heathrow to Rome on 9 February for the FAO forestry committee. Premium economy is only £18 more than economy, which "
    "is good value for money, so I'd like that; if the policy doesn't allow it, economy.",
    trip(traveller_name="Matthew Osei", traveller_title="Forestry Policy Adviser", origin="LHR", destination="FCO",
         travel_date="2027-02-09", booking_date="2027-01-18", business_starts="2027-02-09 16:00",
         purpose="FAO forestry committee in Rome", requested_cabin="PREMIUM_ECONOMY",
         sign_offs=[air("Helen Ashworth", "Approved: fly to Rome for the forestry committee.")]),
    search("LHR", "FCO", "2027-02-09", {
        "morning": {"carrier": "BA", "depart": "08:05"},
        "noon": {"carrier": "BA", "depart": "11:20"},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 14200),
        offer("morning-premium", "morning", "PREMIUM_ECONOMY", 16000),
        offer("noon-economy", "noon", "ECONOMY", 15600),
        offer("noon-premium", "noon", "PREMIUM_ECONOMY", 17400),
    ]),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], DECLINED, ON_FILE, AIR),
    [UNDER, LOWEST, PRIOR],
    "A 135-minute flight: 'less than 5 hours', so economy class only (line 204); premium economy is declined however "
    "small the difference. Value for money permits Eurostar Standard Premier (lines 221-222), a rail rule.",
    distractors=[EUROSTAR])

# ===== refusal (2; wagtail-brow is above with its twin) =====

scenario(
    "whinchat-bield", "refusal", ["personal_travel", "outside_air_section"],
    "Can you book me Gatwick to Madrid on 2 April? It's my sister's wedding and my leave is approved. I'll have my "
    "laptop with me in case anything comes up at work.",
    trip(traveller_name="Laura Bennett", traveller_title="Water Quality Analyst", origin="LGW", destination="MAD",
         travel_date="2027-04-02", booking_date="2027-03-08", business_starts="2027-04-03 15:00",
         purpose="Sister's wedding in Madrid, on annual leave", purpose_kind="PERSONAL", date_fixed=True,
         sign_offs=[sign("MANAGER", "Helen Ashworth", "ANNUAL_LEAVE", "GIVEN", "Leave approved, 2 to 9 April.")]),
    search("LGW", "MAD", "2027-04-02", {
        "iberia": {"carrier": "IB", "depart": "09:15"},
        "british": {"carrier": "BA", "depart": "10:40"},
    }, [
        offer("iberia-economy", "iberia", "ECONOMY", 9800),
        offer("british-economy", "british", "ECONOMY", 11200),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ON_FILE,
             ["INTRODUCTION", "PRINCIPLES", "PURPOSE", "SCOPE"]),
    [OFFICIAL, PURPOSE],
    "Lines 40-43: departments reimburse only expenses actually and necessarily incurred in the course of official "
    "business, and the policy covers travel in the course of official business (lines 69-71). A wedding on annual leave "
    "is not official business, laptop or not: the department buys no ticket. The manager's leave approval is not an "
    "approval of travel.")

# ===== flag (3) =====

scenario(
    "woodruff-staithe", "flag", ["approval_required", "dearer_option"],
    "Heathrow to Johannesburg on 23 March for the SADC biodiversity forum, which starts on the 25th. I'd like business "
    "class; I've asked my line manager to approve it but she hasn't answered yet.",
    trip(traveller_name="Ruth Adebayo", traveller_title="Biodiversity Partnerships Manager", origin="LHR",
         destination="JNB", travel_date="2027-03-23", booking_date="2027-02-24", business_starts="2027-03-25 09:00",
         purpose="SADC biodiversity forum in Johannesburg", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
         sign_offs=[air("Helen Ashworth", "Approved: fly to Johannesburg for the forum."),
                    sign("MANAGER", "Helen Ashworth", "BUSINESS_CLASS", "AWAITED")]),
    search("LHR", "JNB", "2027-03-23", {
        "british": {"carrier": "BA", "depart": "18:40", "minutes": [680]},
        "southafrican": {"carrier": "SA", "depart": "20:15", "minutes": [690]},
    }, [
        offer("british-economy", "british", "ECONOMY", 63800),
        offer("british-business", "british", "BUSINESS", 342000),
        offer("southafrican-economy", "southafrican", "ECONOMY", 59600),
        offer("southafrican-business", "southafrican", "BUSINESS", 318000),
    ]),
    expected("FLAG_FOR_APPROVAL", ["southafrican-business"], ["BUSINESS"],
             ["APPROVAL_REQUIRED", "INTERNATIONAL_LONG_FLIGHT"], ["MANAGER"], AIR),
    [OVER, LOWEST, PRIOR],
    "680 and 690 minutes: over 10 hours, so a business class flight may be purchased 'subject to approval from a "
    "manager or approver' (lines 211-212). The manager approved the air travel but has not answered on business class: "
    "hold the cheapest business fare for her approval. Approval required, not 'no compliant offer'.",
    flag_twins=["kingcup-beck", "merlin-garth"],
    ambiguity="none: an approval is required and missing; the text is clear")

cairo("bluebell-dene", "flag", 300,
      expected("FLAG_FOR_APPROVAL", ["egyptair-business", "egyptair-economy"], ["BUSINESS", "ECONOMY"],
               UNCLEAR_REASONS, UNCLEAR_ROLES, UNCLEAR_CLAUSES, "For journeys of between 5 hours and 10 hours"),
      "300-minute nonstops: exactly 5 hours. Not 'less than 5 hours', so line 204 does not require economy; but the text "
      "does not say whether 'between 5 hours and 10 hours' (line 205) includes 5 hours. If it does, the traveller works "
      "on arrival and may have business; if not, no line allows business. Hold either reading's fare; line management "
      "approves travel outside the policy (lines 86-88).",
      flag_twins=["hawthorn-ings", "hornbeam-sett"], name="Kwame Asante", overlays=["unclear_phrase"],
      ambiguity={"phrase": "For journeys of between 5 hours and 10 hours",
                 "readings": [("'between' includes 5 hours: the journey is in the 5-10 hour band and the traveller "
                               "works on arrival, so book the cheapest business fare"),
                              ("'between' starts after 5 hours: exactly 5 hours is in no band that allows business, so "
                               "book the cheapest economy fare")]})

scenario(
    "campion-wold", "flag", ["multi_leg", "unclear_phrase", "dearer_option"],
    "Edinburgh to Rome on 24 February: I go straight from the airport into the FAO fisheries committee session at "
    "14:30. Business class if the policy allows it; otherwise economy.",
    trip(traveller_name="Iain Cameron", traveller_title="Sea Fisheries Negotiator", origin="EDI", destination="FCO",
         travel_date="2027-02-24", booking_date="2027-01-27", business_starts="2027-02-24 14:30",
         purpose="FAO Committee on Fisheries session in Rome", purpose_kind="NEGOTIATION", requested_cabin="BUSINESS",
         straight_to_work=True,
         sign_offs=[air("Helen Ashworth", "Approved: fly to Rome for the fisheries committee.")]),
    search("EDI", "FCO", "2027-02-24", {
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "06:30", "minutes": [105, 100], "layovers": [115]},
        "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "07:00", "minutes": [80, 125], "layovers": [110]},
    }, [
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 21800),
        offer("frankfurt-business", "frankfurt", "BUSINESS", 68500),
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 19600),
        offer("amsterdam-business", "amsterdam", "BUSINESS", 72400),
    ]),
    expected("FLAG_FOR_APPROVAL", ["amsterdam-economy", "frankfurt-business"], ["BUSINESS", "ECONOMY"],
             UNCLEAR_REASONS, UNCLEAR_ROLES, UNCLEAR_CLAUSES,
             "Air travel for journeys of less than 5 hours should be via economy class only."),
    [UNDER, BETWEEN, LOWEST, PRIOR, OUTSIDE],
    "Both itineraries connect: the flights add up to 205 minutes, but from first departure to last arrival the journey "
    "takes 320 (Frankfurt) or 315 (Amsterdam) minutes. The handbook does not say how a journey is measured. By flying "
    "time it is under 5 hours and economy only (line 204); from first departure to last arrival it is between 5 and 10 hours and the traveller "
    "works on arrival, so business may be bought (lines 205-209). Hold either reading's fare.",
    flag_twins=["nightjar-holm", "ouzel-scarp"],
    ambiguity={"phrase": "Air travel for journeys of less than 5 hours should be via economy class only.",
               "readings": ["a journey is the time in the air: 205 minutes, under 5 hours, so the cheapest economy fare",
                            ("a journey runs from first departure to last arrival, the connection included: over 5 hours "
                             "with work on arrival, so the cheapest business fare")]})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
