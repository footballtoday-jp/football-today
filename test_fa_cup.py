from urllib.request import Request, urlopen
import re
from html import unescape

URL = "https://thefa.com/competitions/thefacup/fixtures"

print("Testing FA Cup official fixtures...")
print("URL:", URL)

req = Request(
    URL,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
    }
)

with urlopen(req, timeout=90) as response:
    html = response.read().decode("utf-8", errors="ignore")

print("HTTP download: SUCCESS")
print("HTML size:", len(html))

# HTMLタグを簡単に除去して文字列化
text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = unescape(text)
text = re.sub(r"\s+", " ", text)

# FA Cupページに試合情報が含まれているか確認
keywords = [
    "Fixtures",
    "Preliminary Round",
    "Redcar Town",
    "Bridlington Town",
]

print("\nChecking fixture data...")

for keyword in keywords:
    if keyword.lower() in text.lower():
        print("FOUND:", keyword)
    else:
        print("NOT FOUND:", keyword)

print("\nSample around Redcar Town:")

pos = text.lower().find("redcar town")

if pos >= 0:
    print(text[max(0, pos - 150):pos + 300])
else:
    print("Redcar Town was not found.")

print("\nTEST FINISHED")
