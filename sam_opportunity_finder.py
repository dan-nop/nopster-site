"""
sam_opportunity_finder.py

Pulls active SAM.gov contract opportunities for a given NAICS code and
flags ones that are likely NOT realistically biddable (sole-source,
tied to a named incumbent/OEM, wrong set-aside category, etc.).

v2 changes:
- Fixed the actual filter param: it's `ncode`, not `naicsCode`. This was
  silently ignored before, which is why unrelated results (trailers, HVAC,
  ship charters) were showing up regardless of NAICS code.
- Fetches the REAL notice description text (a second API call per listing)
  instead of just scanning the title, since the search endpoint only
  returns a link to the description, not the text itself.
- Sanity check: warns you if any returned result's naicsCode doesn't
  actually match what you searched for, so a broken filter can't go
  unnoticed again.
- Adds agency/department and solicitation number columns for more context.
- Saves output to local/sam_opportunities.csv (creates the folder if it
  doesn't exist) so it's easy to gitignore.

SETUP
------
1. pip install requests python-dotenv python-dateutil
2. Create a `.env` file in this folder (DO NOT COMMIT IT):
       SAM_API_KEY=your_actual_key_here
3. Run: python3 sam_opportunity_finder.py

v3 changes:
- Flags DoD agencies (Army, Navy, Air Force, DLA, SOCOM, etc.) separately,
  since you've opted out of DoD work for now — checked against the agency
  field only, so it won't false-positive on things like "Department of
  Veterans Affairs."
- Adds a `days_until_due` column so you can triage by urgency at a glance.
- Automatically skips any listing whose response deadline has already
  passed (a safety net, shouldn't normally trigger given the date range,
  but guards against edge cases).
- Sort order is now: clean listings first, then soonest-deadline first
  within each group.
"""

import os
import csv
import time
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SAM_API_KEY")
if not API_KEY:
    raise SystemExit(
        "No API key found. Create a .env file with SAM_API_KEY=your_key_here"
    )

# ---- Search settings -------------------------------------------------

NAICS_CODE = "541511"          # Custom Computer Programming Services
DAYS_BACK = 14
NOTICE_TYPES = "o,p,k,r"       # Solicitation, Presolicitation, Combined Synopsis, Sources Sought
LIMIT_PER_PAGE = 100

SEARCH_URL = "https://api.sam.gov/opportunities/v2/search"

OUTPUT_DIR = "local"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sam_opportunities.csv")

# ---- Red flags ---------------------------------------------------------

RED_FLAG_KEYWORDS = {
    "sole source": "Sole-source (already awarded to a named vendor)",
    "justification for other than full and open competition": "Sole-source justification attached",
    "8(a)": "8(a)-specific set-aside",
    "sdvosb": "Service-Disabled Veteran-Owned set-aside",
    "wosb": "Woman-Owned set-aside",
    "hubzone": "HUBZone-specific set-aside",
    "authorization letter": "Requires OEM/incumbent authorization to bid",
    "proprietary": "Tied to proprietary/incumbent system",
    "incumbent": "References an incumbent contractor",
    "oem": "References an OEM requirement",
}

# Agencies to flag as DoD -- checked against the "agency" (fullParentPathName)
# field only, so this won't accidentally catch "Department of Veterans
# Affairs" or similar non-DoD agencies that happen to share words.
# Note: SAM.gov's actual data uses abbreviated top-level names like
# "DEPT OF DEFENSE.DEPT OF THE ARMY...", not full spelled-out names --
# so checking for the top-level "dept of defense" alone catches every
# DoD sub-agency underneath it, which is simpler and more reliable than
# trying to enumerate every sub-agency name/format.
DOD_AGENCY_KEYWORDS = [
    "dept of defense",
    "department of defense",
]


def build_date_range():
    today = datetime.today()
    start = today - timedelta(days=DAYS_BACK)
    return start.strftime("%m/%d/%Y"), today.strftime("%m/%d/%Y")


def fetch_opportunities():
    posted_from, posted_to = build_date_range()
    all_results = []
    offset = 0

    while True:
        params = {
            "api_key": API_KEY,
            "ncode": NAICS_CODE,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "ptype": NOTICE_TYPES,
            "limit": LIMIT_PER_PAGE,
            "offset": offset,
        }
        resp = requests.get(SEARCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        batch = data.get("opportunitiesData", [])
        all_results.extend(batch)

        total = data.get("totalRecords", 0)
        offset += LIMIT_PER_PAGE
        if offset >= total or not batch:
            break

    return all_results


def fetch_description_text(description_url):
    """Search results only give a link to the real description.
    Fetch it, respecting SAM.gov's ~1 request/second guidance."""
    if not description_url:
        return ""
    try:
        resp = requests.get(
            description_url,
            params={"api_key": API_KEY},
            timeout=20,
        )
        time.sleep(1)  # be polite to the API
        if resp.status_code != 200:
            return ""
        data = resp.json()
        return data.get("description", "") if isinstance(data, dict) else ""
    except (requests.RequestException, ValueError):
        return ""


def flag_opportunity(title, set_aside, full_text, agency):
    text = f"{title or ''} {set_aside or ''} {full_text or ''}".lower()
    flags = []
    for keyword, reason in RED_FLAG_KEYWORDS.items():
        if keyword in text:
            flags.append(reason)

    agency_text = (agency or "").lower()
    if any(kw in agency_text for kw in DOD_AGENCY_KEYWORDS):
        flags.append("DoD agency (you're not currently pursuing DoD work)")

    return flags


def days_until_due(response_deadline):
    """Returns an integer day count until the response deadline, or None
    if it can't be parsed. Negative means it's already past due."""
    if not response_deadline:
        return None
    try:
        due = dateparser.parse(response_deadline)
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (due - now).days
    except (ValueError, TypeError):
        return None


def main():
    print(f"Fetching opportunities for NAICS {NAICS_CODE}, last {DAYS_BACK} days...")
    results = fetch_opportunities()
    print(f"Found {len(results)} total opportunities from the API.")

    mismatched = [r for r in results if r.get("naicsCode") != NAICS_CODE]
    if mismatched and len(mismatched) == len(results):
        print(
            f"\n⚠️  WARNING: NONE of the {len(results)} results match NAICS "
            f"{NAICS_CODE}. The filter is likely broken again — check the "
            f"'ncode' parameter and API response before trusting this output.\n"
        )
    elif mismatched:
        print(f"Note: {len(mismatched)} results had an unexpected NAICS code — keeping them, but worth spot-checking.")

    print("Fetching full descriptions for red-flag scanning (this takes a bit, ~1/sec)...")

    rows = []
    for i, item in enumerate(results, 1):
        title = item.get("title", "")
        notice_id = item.get("noticeId", "")
        notice_type = item.get("type", "")
        naics = item.get("naicsCode", "")
        sol_number = item.get("solicitationNumber", "")
        agency = item.get("fullParentPathName", "")
        posted_date = item.get("postedDate", "")
        response_date = item.get("responseDeadLine", "")
        set_aside = item.get("typeOfSetAsideDescription", "")
        description_url = item.get("description", "")
        ui_link = item.get("uiLink", "")

        print(f"  [{i}/{len(results)}] {title[:60]}")
        full_text = fetch_description_text(description_url)

        days_left = days_until_due(response_date)

        # Skip anything whose response deadline has already passed
        if days_left is not None and days_left < 0:
            print(f"      (skipping — response deadline already passed)")
            continue

        flags = flag_opportunity(title, set_aside, full_text, agency)

        rows.append({
            "title": title,
            "agency": agency,
            "notice_id": notice_id,
            "solicitation_number": sol_number,
            "type": notice_type,
            "naics_code": naics,
            "set_aside": set_aside,
            "posted_date": posted_date,
            "response_deadline": response_date,
            "days_until_due": days_left if days_left is not None else "",
            "flags": "; ".join(flags) if flags else "",
            "looks_clean": "YES" if not flags else "NO",
            "link": ui_link,
        })

    # Clean ones first, then soonest deadline first within each group
    rows.sort(key=lambda r: (r["looks_clean"] != "YES", r["days_until_due"] if isinstance(r["days_until_due"], int) else 9999))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else [
        "title", "agency", "notice_id", "solicitation_number", "type",
        "naics_code", "set_aside", "posted_date", "response_deadline",
        "days_until_due", "flags", "looks_clean", "link",
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    clean_count = sum(1 for r in rows if r["looks_clean"] == "YES")
    print(f"\nSaved {len(rows)} opportunities to {OUTPUT_FILE}")
    print(f"{clean_count} of them look clean (no red flags) — check those first.")


if __name__ == "__main__":
    main()
