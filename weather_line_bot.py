#!/usr/bin/env python3
import os, json, datetime, logging, requests, pytz
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import ImageSendMessage

JST = pytz.timezone("Asia/Tokyo")
logging.basicConfig(level=logging.INFO)

def read_locations():
    with open("locations.json", encoding="utf-8") as f:
        return json.load(f)

def get_weather(lat, lon):
    key = os.environ["WEATHER_API_KEY"]
    r = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}"
        f"&units=metric&lang=ja&appid={key}", timeout=10
    )
    r.raise_for_status()
    d = r.json()
    return d["weather"][0]["description"], d["main"]["temp"]

def gen_image(desc, temp, city):
    prompt = (
        f"Flat minimal illustration of {city} weather on "
        f"{datetime.datetime.now(JST):%Y-%m-%d}: {desc}, {temp:.1f}°C, "
        "soft pastel palette, Japanese
