import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

LEAGUE_ID = "4481"
SEASON = "2026-2027"

params = urlencode({
    "id": LEAGUE_ID,
    "s": SEASON,
})

url = (
    "https://www.thesportsdb.com/api/v1/json/123/"
    f"eventsseason.php?{params}"
)

print("Testing TheSportsDB...")
print("League ID:", LEAGUE_ID)
print("Season:", SEASON)

req = Request(
    url,
    headers={
        "User-Agent": "football-today-test"
    }
)

with urlopen(req, timeout=30) as response:
    data = json.load(response)

events = data.get("events") or []

print("Number of events:", len(events))

if not events:
    print("No events returned.")
else:
    print("SUCCESS: Events were returned!")

    for event in events[:10]:
        print("--------------------")
        print("Date:", event.get("dateEvent"))
        print("Time:", event.get("strTime"))
        print("Home:", event.get("strHomeTeam"))
        print("Away:", event.get("strAwayTeam"))
        print("Season:", event.get("strSeason"))
