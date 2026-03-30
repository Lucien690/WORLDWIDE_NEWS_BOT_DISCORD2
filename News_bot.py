import discord
import requests
import asyncio
import os

TOKEN = os.getenv("TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

CHANNEL_ID = 1475125646064619541

client = discord.Client(intents=discord.Intents.default())
sent_news = set()

KEYWORDS = [
    "war", "attack", "missile", "china", "taiwan", "russia",
    "oil", "opec", "bank", "collapse", "crisis", "default",
    "inflation", "interest rate", "fed", "ecb",
    "bitcoin", "crypto", "stock", "nasdaq", "sp500",
    "gold", "silver"
]

def get_news():
    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("API ERROR:", response.text)
        return []

    return response.json().get("articles", [])

def is_important(title):
    title = title.lower()
    return any(word in title for word in KEYWORDS)

def analyze_news(title):
    t = title.lower()

    if any(x in t for x in ["war", "attack", "missile"]):
        return "🚨 EXTREME – Risk-Off (Gold 📈, Stocks 📉)"
    
    if any(x in t for x in ["bank", "collapse", "crisis"]):
        return "🏦 Banken Risiko – Märkte unsicher"
    
    if "oil" in t or "opec" in t:
        return "🛢️ Öl Bewegung erwartet"
    
    if any(x in t for x in ["fed", "interest rate"]):
        return "🏦 Zentralbank Einfluss"

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

                if not title or title in sent_news:
                    continue

                if not is_important(title):
                    continue

                analysis = analyze_news(title)

                embed = discord.Embed(
                    title="🌍 Breaking Market News",
                    description=title,
                    color=discord.Color.orange()
                )

                embed.add_field(name="📊 Analyse", value=analysis, inline=False)
                embed.add_field(name="🔗 Link", value=url, inline=False)

                await channel.send(embed=embed)

                sent_news.add(title)

        except Exception as e:
            print("ERROR:", e)

        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f"BOT ONLINE: {client.user}")
    client.loop.create_task(news_loop())

client.run(TOKEN)
