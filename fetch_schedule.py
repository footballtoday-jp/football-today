#!/usr/bin/env python3
import json, os, sys
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from zoneinfo import ZoneInfo

API = "https://api.football-data.org/v4/matches"
TOKEN = os.environ.get("FOOTBALL_DATA_API_KEY")
if not TOKEN:
    raise SystemExit("FOOTBALL_DATA_API_KEY is not set")

JST = ZoneInfo("Asia/Tokyo")
today = datetime.now(JST).date()
date_from = today
date_to = today + timedelta(days=9)

# Current Free plan coverage used by this first version.
# Belgium/Europa League are intentionally not requested here because they
# are not listed in the current Free coverage page.
COMPETITIONS = "PL,PD,SA,BL1,FL1,DED,CL"

# Japanese players / clubs. This is deliberately maintained as a small
# mapping so the public site never exposes the API token.
JP_PLAYERS = {
   # Premier League
   "brighton & hove albion": ["三笘薫"],
   "liverpool fc": ["遠藤航"],
   "crystal palace fc": ["鎌田大地", "冨安健洋"],
   "leeds united fc": ["田中碧"],
   "tottenham hotspur fc": ["高井幸大"],
   "ipswich town fc": ["前田大然"],
    "hull city": ["守田英正"],
    "aston villa fc": ["鈴木彩艶"],
    "coventry city": ["坂元達裕"],

    # La Liga
    "real sociedad de fútbol": ["久保建英"],
    "valencia cf": ["佐藤龍之介"],

    # Serie A
    # 現時点では登録なし

    # Bundesliga
    "fc bayern münchen": ["伊藤洋輝"],
    "sv werder bremen": [],
    "eintracht frankfurt": ["堂安律", "小杉啓太"],
    "sc freiburg": ["鈴木唯人", "山本理仁", "長田澪", "後藤啓介"],
    "1. fsv mainz 05": ["川﨑颯太", "佐野海舟"],
    "borussia mönchengladbach": ["町野修斗", "宇野禅斗", "橋岡大樹", "板倉滉"],

    # Ligue 1
    "le havre ac": ["瀬古歩夢", "水多海斗"],
    "stade de reims": ["中村敬斗"],

    # Eredivisie
    "feyenoord rotterdam": ["渡辺剛", "上田綺世"],
    "nec nijmegen": ["小川航基"],
    "psv": ["佐野航大"],
}

ALIASES = {
    "brighton & hove albion": "ブライトン",
    "brighton & hove albion fc": "ブライトン",
    "liverpool fc": "リヴァプール",
    "crystal palace fc": "クリスタル・パレス",
    "leeds united fc": "リーズ・ユナイテッド",
    "tottenham hotspur fc": "トッテナム",
    "aston villa fc": "アストン・ヴィラ",
    "coventry city": "コヴェントリー・シティ",
    "ipswich town fc": "イプスウィッチ・タウン",
    "real sociedad de fútbol": "レアル・ソシエダ",
    "valencia cf": "バレンシア",
    "parma calcio 1913": "パルマ",
    "fc bayern münchen": "バイエルン・ミュンヘン",
    "sv werder bremen": "ブレーメン",
    "eintracht frankfurt": "フランクフルト",
    "sc freiburg": "フライブルク",
    "1. fsv mainz 05": "マインツ",
    "borussia mönchengladbach": "ボルシアMG",
    "le havre ac": "ル・アーヴル",
    "stade de reims": "スタッド・ランス",
    "afc ajax": "アヤックス",
    "feyenoord rotterdam": "フェイエノールト",
    "nec nijmegen": "NECナイメヘン",
    "psv": "PSV",
}

LEAGUE_JA = {
    "PL":"🇬🇧 プレミアリーグ",
    "PD":"🇪🇸 ラ・リーガ",
    "SA":"🇮🇹 セリエA",
    "BL1":"🇩🇪 ブンデスリーガ",
    "FL1":"🇫🇷 リーグ・アン",
    "DED":"🇳🇱 エールディヴィジ",
    "CL":"🇪🇺 UEFAチャンピオンズリーグ",
}

def norm(s):
    return " ".join(s.lower().strip().split())
    
def alias_name(name):
    n = norm(name)
    for key, value in ALIASES.items():
        if norm(key) == n:
            return value
    return name
    
def get_json(url):
    req=Request(url, headers={"X-Auth-Token": TOKEN, "Accept":"application/json"})
    try:
        with urlopen(req, timeout=30) as r:
            return json.load(r)
    except HTTPError as e:
        body=e.read().decode("utf-8","replace")
        raise RuntimeError(f"football-data.org HTTP {e.code}: {body[:500]}")

def fetch_page(offset=0):
    url=(f"{API}?competitions={COMPETITIONS}"
         f"&dateFrom={date_from.isoformat()}&dateTo={date_to.isoformat()}"
         f"&limit=100&offset={offset}")
    return get_json(url)

matches=[]
offset=0
while True:
    data=fetch_page(offset)
    page=data.get("matches",[])
    matches.extend(page)
    if len(page)<100:
        break
    offset += len(page)

out=[]
for m in matches:
    comp=m.get("competition",{})
    code=comp.get("code")
    if code not in LEAGUE_JA:
        continue
    utc=m["utcDate"]
    dt=datetime.fromisoformat(utc.replace("Z","+00:00")).astimezone(JST)
    home=m["homeTeam"]["name"]
    away=m["awayTeam"]["name"]
    hn=norm(home); an=norm(away)
    hjp=JP_PLAYERS.get(hn,[])
    ajp=JP_PLAYERS.get(an,[])
    out.append({
        "dateJst": dt.date().isoformat(),
        "timeJst": dt.strftime("%H:%M"),
        "utcDate": utc,
        "competition": code,
        "league": LEAGUE_JA[code],
        "homeNameJa": alias_name(home),
        "awayNameJa": alias_name(away),
        "homeJp": hjp,
        "awayJp": ajp,
    })

out.sort(key=lambda x:(x["dateJst"], x["utcDate"]))
with open("schedule.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)

print(f"wrote {len(out)} matches: {date_from} .. {date_to}")
