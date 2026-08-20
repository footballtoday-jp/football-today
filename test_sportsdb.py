import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

DATE = "2026-07-09"

params = urlencode({
    "d": DATE,
    "s": "Soccer",
})

url = (
    "https://www.thesportsdb.com/api/v1/json/123/"
    f"eventsday.php?{params}"
)

print("Testing TheSportsDB by date...")
print("Date:", DATE)

req = Request(
    url,
    headers={
        "User-Agent": "football-today-test"
    }
)

with urlopen(req, timeout=30) as response:
    data = json.load(response)

events = data.get("events") or []

print("All soccer events returned:", len(events))

# UEFA Europa Leagueだけを抽出
el_events = []

for event in events:
    league = (event.get("strLeague") or "").lower()

    if "europa league" in league:
        el_events.append(event)

print("Europa League events:", len(el_events))

if not el_events:
    print("No Europa League events returned.")
else:
    print("SUCCESS: Europa League events were returned!")

    for event in el_events:
        print("--------------------")
        print("League:", event.get("strLeague"))
        print("Date:", event.get("dateEvent"))
        print("Time:", event.get("strTime"))
        print("Home:", event.get("strHomeTeam"))
        print("Away:", event.get("strAwayTeam"))
