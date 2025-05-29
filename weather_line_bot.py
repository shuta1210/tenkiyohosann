#!/usr/bin/env python3
"""
複数地点の今日の天気を取得し、OpenAI で画像を生成して
LINE 公式アカウントから自分へ画像を送るスクリプト。
"""
import os
import json
import datetime
import logging
import requests
import pytz
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import ImageSendMessage

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
    prompt = (
        f"Flat minimal illustration of {city} weather on "
        f"{datetime.datetime.now(JST):%Y-%m-%d}: {desc}, {temp:.1f}°C, "
        "soft pastel palette, Japanese style date text."
    )
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    res = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return res.data[0].url

def send_line(image_url):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]
    line_bot = LineBotApi(token)
    message = ImageSendMessage(original_content_url=image_url,
                               preview_image_url=image_url)
    line_bot.push_message(user_id, message)

def main():
    for loc in read_locations():
        desc, temp = get_weather(loc["lat"], loc["lon"])
        url = gen_image(desc, temp, loc["name"])
        send_line(url)

if __name__ == "__main__":
    main()
