from urllib.request import Request, urlopen
import re
from html import unescape

URL = "https://www.thefa.com/competitions/thefacup/fixtures"

print("Testing FA Cup official fixtures...")
print("URL:", URL)

req = Request(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urlopen(req, timeout=30) as response:
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
