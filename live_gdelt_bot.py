import discord
import requests
import asyncio
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1475125736665776128

client = discord.Client(intents=discord.Intents.default())
sent_news = set()

KEYWORDS = [
"war", "conflict", "attack", "strike", "missile", "explosion",
"military", "invasion", "airstrike", "drone", "nuclear",
"russia", "ukraine", "china", "taiwan",
"iran", "israel", "usa", "united states",
"europe", "eu", "germany", "france",
"middle east", "nato",
"oil", "crude", "brent", "wti", "refinery", "pipeline",
"gas", "energy", "opec",
"gold", "silver", "precious metals", "bullion", "safe haven",
"bank", "banking", "collapse", "financial crisis",
"liquidity crisis", "blackrock", "jpmorgan",
"goldman sachs", "central bank", "fed", "ecb",
"bitcoin", "crypto", "ethereum", "binance", "coinbase"
]

def get_news():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
    "query": "war OR oil OR gold OR crypto OR bank OR russia OR china OR iran OR israel OR usa OR europe",
    "mode": "ArtList",
    "maxrecords": 30,
    "format": "json",
    "sort": "DateDesc"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
    print("API ERROR:", response.text)
    return []

    return response.json().get("articles", [])


def get_score(title):
t = title.lower()
score = 0

if any(x in t for x in ["war", "attack", "missile", "strike", "invasion"]):
score += 3

if any(x in t for x in ["oil", "opec", "refinery"]):
score += 2

if any(x in t for x in ["bank", "collapse", "crisis", "blackrock"]):
score += 2

if any(x in t for x in ["gold", "silver"]):
score += 2

if any(x in t for x in ["russia", "china", "iran", "israel", "usa"]):
score += 1

if any(x in t for x in ["crypto", "bitcoin"]):
score += 1

return score


def analyze(title):
t = title.lower()

if any(x in t for x in ["war", "attack", "missile", "strike"]):
return "🚨 KRIEG → Gold 📈 | Öl 📈 | Aktien 📉 | Crypto 📉"

if any(x in t for x in ["oil", "opec", "refinery"]):
return "🛢️ ÖL → Inflation steigt | Märkte unter Druck"

if any(x in t for x in ["bank", "collapse", "crisis"]):
return "🏦 BANKENRISIKO → Markt instabil | Aktien 📉 | Gold 📈"

if any(x in t for x in ["gold", "silver"]):
return "🪙 GOLD / SILBER → Safe Haven Bewegung 📈"

if any(x in t for x in ["crypto", "bitcoin"]):
return "₿ CRYPTO → Hohe Volatilität ⚡"

return "⚠️ Marktbewegung möglich"


async def news_loop():
await client.wait_until_ready()
channel = await client.fetch_channel(CHANNEL_ID)

while not client.is_closed():
try:
articles = get_news()

for article in articles:
title = article.get("title", "")
url = article.get("url", "")

if not title:
continue

title_clean = title.lower()

if title_clean in sent_news:
continue

if not any(word in title_clean for word in KEYWORDS):
continue

score = get_score(title)

if score < 3:
continue

analysis = analyze(title)

embed = discord.Embed(
title="🚨 LIVE MARKET ALERT",
description=title,
color=discord.Color.red()
)

embed.add_field(name="📊 Analyse", value=analysis, inline=False)
embed.add_field(name="🔥 Impact Score", value=str(score), inline=False)
embed.add_field(name="🔗 Link", value=url, inline=False)

content = None
if score >= 4:
content = "@everyone 🚨 EXTREME NEWS"

await channel.send(content=content, embed=embed)

sent_news.add(title_clean)

except Exception as e:
print("ERROR:", e)

await asyncio.sleep(90)


@client.event
async def on_ready():
print(f"LIVE GDELT BOT ONLINE: {client.user}")
client.loop.create_task(news_loop())


client.run(TOKEN)
