import csv
import io
from urllib.request import Request, urlopen

URL = (
    "https://raw.githubusercontent.com/"
    "olbauday/FPL-Core-Insights/main/"
    "data/2026-2027/By%20Gameweek/GW1/fixtures.csv"
)

print("Testing FPL-Core-Insights...")
print("Downloading fixtures.csv...")

req = Request(
    URL,
    headers={"User-Agent": "football-today-test"}
)

with urlopen(req, timeout=30) as response:
    text = response.read().decode("utf-8-sig")

rows = list(csv.DictReader(io.StringIO(text)))

print("Number of fixtures:", len(rows))

if not rows:
    print("No fixtures returned.")
else:
    print("SUCCESS: fixtures.csv was downloaded!")

    print("Columns:")
    print(list(rows[0].keys()))

    print("\nFirst fixtures:")

    for row in rows[:10]:
        print("--------------------")
        print("Tournament:", row.get("tournament"))
        print("Kickoff:", row.get("kickoff_time"))
        print("Home:", row.get("home_team_name"))
        print("Away:", row.get("away_team_name"))
