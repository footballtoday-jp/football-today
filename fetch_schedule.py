#!/usr/bin/env python3
import json, os, sys, time
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
date_to = today + timedelta(days=10)

# Current Free plan coverage used by this first version.
# Belgium/Europa League are intentionally not requested here because they
# are not listed in the current Free coverage page.
COMPETITIONS = "PL,ELC,PD,SA,BL1,FL1,DED,CL"

# Japanese players / clubs. This is deliberately maintained as a small
# mapping so the public site never exposes the API token.
JP_PLAYERS = {
   # Premier League
   "brighton & hove albion": ["三笘薫"],
   "brighton & hove albion fc": ["三笘薫"],
   "liverpool fc": ["遠藤航"],
   "crystal palace fc": ["鎌田大地", "冨安健洋"],
   "leeds united fc": ["田中碧"],
   "tottenham hotspur fc": ["高井幸大"],
   "ipswich town fc": ["前田大然"],
   "hull city afc": ["守田英正"],
   "aston villa fc": ["鈴木彩艶"],
   "coventry city fc": ["坂元達裕"],
    
    # Championship
    "southampton fc": ["菅原由勢", "松木玖生"],
    "blackburn rovers fc": ["大橋祐紀", "森下龍矢"],
    "birmingham city fc": ["岩田智輝", "藤本寛也"],
    "queens park rangers fc": ["斉藤光毅"],
    "bristol city fc": ["平河悠"],
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
    "fc schalke 04": ["田中聡"],
    "tsg 1899 hoffenheim": ["町田浩樹"],
    "borussia dortmund": ["山本天翔"],

    # Ligue 1
    "le havre ac": ["瀬古歩夢", "水多海斗","中村草太"],
    "as monaco fc": ["南野拓実"],
    "as monaco": ["南野拓実"],

    # Eredivisie
    "feyenoord rotterdam": ["渡辺剛", "上田綺世"],
    "nec nijmegen": ["小川航基"],
    "psv": ["佐野航大"],
    "az": ["毎熊晟矢", "市原吏音"],
    "sparta rotterdam": ["三戸舜介"],
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
    "coventry city fc": "コヴェントリー・シティ",
    "ipswich town fc": "イプスウィッチ・タウン",
    "hull city afc": "ハル・シティ",
    
     # Championship
    "southampton fc": "サウサンプトン",
    "blackburn rovers fc": "ブラックバーン",
    "birmingham city fc": "バーミンガム",
    "queens park rangers fc": "QPR",
    "bristol city fc": "ブリストル・シティ",
    
    "real sociedad de fútbol": "レアル・ソシエダ",
    "valencia cf": "バレンシア",
    "parma calcio 1913": "パルマ",
    "fc bayern münchen": "バイエルン・ミュンヘン",
    "sv werder bremen": "ブレーメン",
    "eintracht frankfurt": "フランクフルト",
    "sc freiburg": "フライブルク",
    "1. fsv mainz 05": "マインツ",
    "borussia mönchengladbach": "ボルシアMG",
    "tsg 1899 hoffenheim": "ホッフェンハイム",
    "borussia dortmund": "ドルトムント",
    "as monaco fc": "モナコ",
    "as monaco": "モナコ",
    "le havre ac": "ル・アーヴル",
    "stade de reims": "スタッド・ランス",
    "afc ajax": "アヤックス",
    "feyenoord rotterdam": "フェイエノールト",
    "nec nijmegen": "NECナイメヘン",
    "psv": "PSV",
    "sparta rotterdam": "スパルタ・ロッテルダム",
}

LEAGUE_JA = {
    "PL":"🇬🇧 プレミアリーグ",
    "ELC":"🏴 EFLチャンピオンシップ",
    "PD":"🇪🇸 ラ・リーガ",
    "SA":"🇮🇹 セリエA",
    "BL1":"🇩🇪 ブンデスリーガ",
    "FL1":"🇫🇷 リーグ・アン",
    "DED":"🇳🇱 エールディヴィジ",
    "CL":"🇪🇺 UEFAチャンピオンズリーグ",
}

ELC_TARGET_TEAMS = {
    "southampton fc",
    "blackburn rovers fc",
    "birmingham city fc",
    "queens park rangers fc",
    "bristol city fc",
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
    print(f"API request start: {url}", flush=True)
    
    for attempt in range(4):
        req = Request(
            url,
            headers={
                "X-Auth-Token": TOKEN,
                "Accept": "application/json"
            }
        )

        try:
            with urlopen(req, timeout=30) as r:
                print(f"API response received: HTTP {r.status}", flush=True)
                return json.load(r)

        except HTTPError as e:
            body = e.read().decode("utf-8", "replace")

            if e.code == 429 and attempt < 3:
                retry_after = e.headers.get("Retry-After")

                try:
                    wait_seconds = int(retry_after) if retry_after else 60
                except (TypeError, ValueError):
                    wait_seconds = 60

                wait_seconds = min(wait_seconds + 5, 90)

                print(
                    f"Rate limit reached. "
                    f"Waiting {wait_seconds} seconds before retry...",
                    flush=True
                )

                time.sleep(wait_seconds)
                continue

            raise RuntimeError(
                f"football-data.org HTTP {e.code}: {body[:500]}"
            )

def fetch_matches():
    url=(
        f"{API}?competitions={COMPETITIONS}"
        f"&dateFrom={date_from.isoformat()}"
        f"&dateTo={date_to.isoformat()}"
    )
    return get_json(url)

data = fetch_matches()
matches = data.get("matches", [])

out=[]
for m in matches:
    comp=m.get("competition",{})
    code=comp.get("code")

    if code not in LEAGUE_JA:
        continue

    if code == "ELC":
        home_name = norm(m["homeTeam"]["name"])
        away_name = norm(m["awayTeam"]["name"])

        if (
            home_name not in ELC_TARGET_TEAMS
            and away_name not in ELC_TARGET_TEAMS
        ):
            continue

    utc=m["utcDate"]
    dt=datetime.fromisoformat(utc.replace("Z","+00:00")).astimezone(JST)
    
    # 6時区切り
    # 00:00～05:59の試合は前日の扱いにする
    display_dt = dt - timedelta(hours=6)

    home=m["homeTeam"]["name"]
    away=m["awayTeam"]["name"]
    hn=norm(home); an=norm(away)
    hjp=JP_PLAYERS.get(hn,[])
    ajp=JP_PLAYERS.get(an,[])
    
    # 6時より前の時間は24時台として表示
    display_hour = dt.hour + 24 if dt.hour < 6 else dt.hour
    display_time = f"{display_hour:02d}:{dt.minute:02d}"

    out.append({
    "dateJst": display_dt.date().isoformat(),
    "timeJst": display_time,
        
        "utcDate": utc,
        "competition": code,
        "league": LEAGUE_JA[code],
        "homeNameJa": alias_name(home),
        "awayNameJa": alias_name(away),
        "homeJp": hjp,
        "awayJp": ajp,
    })

# 手入力カップ戦を追加
if os.path.exists("cup_matches.json"):
    with open("cup_matches.json", "r", encoding="utf-8") as f:
        cup_matches = json.load(f)

    CUP_LEAGUE_JA = {
        "FA": "🏴 FAカップ",
        "EFL": "🏴 カラバオカップ",
        "EL": "🇪🇺 UEFAヨーロッパリーグ",
        "UECL": "🇪🇺 UEFAカンファレンスリーグ",
        "CDR": "🇪🇸 コパ・デル・レイ",
        "DFB": "🇩🇪 DFBポカール",
        "CDF": "🇫🇷 クープ・ドゥ・フランス",
        "KNVB": "🇳🇱 KNVBベーカー",
    }

    for m in cup_matches:
        code = m["competition"]
        home = m["home"]
        away = m["away"]

        home_n = norm(home)
        away_n = norm(away)

        # cup_matches.json の時刻は日本時間として入力
        dt = datetime.fromisoformat(
            f'{m["date"]}T{m["time"]}:00'
        ).replace(tzinfo=JST)

        # 00:00〜05:59は前日の試合として表示
        display_dt = dt - timedelta(hours=6)

        display_hour = dt.hour + 24 if dt.hour < 6 else dt.hour
        display_time = f"{display_hour:02d}:{dt.minute:02d}"

        out.append({
            "dateJst": display_dt.date().isoformat(),
            "timeJst": display_time,
            "utcDate": dt.astimezone(timezone.utc).isoformat(),
            "competition": code,
            "league": CUP_LEAGUE_JA.get(code, code),
            "homeNameJa": alias_name(home),
            "awayNameJa": alias_name(away),
            "homeJp": JP_PLAYERS.get(home_n, []),
            "awayJp": JP_PLAYERS.get(away_n, []),
        })

out.sort(key=lambda x:(x["dateJst"], x["utcDate"]))
with open("schedule.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)

print(f"wrote {len(out)} matches: {date_from} .. {date_to}")
