import os
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

API_KEY = os.environ.get("API_FOOTBALL_KEY")

if not API_KEY:
    raise RuntimeError("API_FOOTBALL_KEY is not set")

BASE_URL = "https://v3.football.api-sports.io"

# 2026-27シーズンのEuropa Leagueを検索
params = urlencode({
    "search": "Europa League",
    "season": 2026,
})

url = f"{BASE_URL}/leagues?{params}"

req = Request(
    url,
    headers={
        "x-apisports-key": API_KEY,
        "Accept": "application/json",
    },
)

print("Searching UEFA Europa League for season 2026...")

with urlopen(req, timeout=30) as response:
    data = json.load(response)

print("Errors:", data.get("errors"))
print("Results:", data.get("results"))

for item in data.get("response", []):
    league = item.get("league", {})
    country = item.get("country", {})

    print("--------------------")
    print("League ID:", league.get("id"))
    print("League name:", league.get("name"))
    print("Type:", league.get("type"))
    print("Country:", country.get("name"))

    seasons = item.get("seasons", [])
    for season in seasons:
        print(
            "Season:",
            season.get("year"),
            "Current:",
            season.get("current"),
        )
