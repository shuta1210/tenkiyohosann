#!/usr/bin/env python3
import os, json, datetime, logging, requests, pytz
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import ImageSendMessage

# タイムゾーン設定
JST = pytz.timezone("Asia/Tokyo")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_locations():
    with open("locations.json", encoding="utf-8") as f:
        return json.load(f)

def get_weather(lat, lon):
    key = os.environ["WEATHER_API_KEY"]
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&units=metric&lang=ja&appid={key}"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["weather"][0]["description"], data["main"]["temp"]

def gen_image(desc, temp, city):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    today = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    prompt = (
        f"Flat minimal illustration of {city} weather on {today}: "
        f"{desc}, {temp:.1f}°C, soft pastel palette, Japanese style date text."
    )
    resp = client.images.generate(prompt=prompt, size="1024x1024", n=1)
    return resp.data[0].url

def main():
    bot = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    for loc in read_locations():
        desc, temp = get_weather(loc["lat"], loc["lon"])
        img_url = gen_image(desc, temp, loc["name"])
        bot.push_message(
            to=os.environ["LINE_USER_ID"],
            messages=[ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)]
        )
        logger.info(f"Sent {loc['name']} → {img_url}")

if __name__ == "__main__":
    main()
