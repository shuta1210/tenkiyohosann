#!/usr/bin/env python3
"""
複数地点の今日の天気を取得し、OpenAI で画像を生成して
LINE 公式アカウントから自分へ画像を送るスクリプト。
locations.json に場所を追加するだけで拡張できる。
"""
import os, json, datetime, logging, requests, pytz, openai

JST = pytz.timezone("Asia/Tokyo")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_locations():
    with open("locations.json", encoding="utf-8") as f:
        return json.load(f)  # [{"name": "...", "lat": .., "lon": ..}, ...]

def get_weather(lat, lon):
    key = os.environ["WEATHER_API_KEY"]
    url = (f"https://api.openweathermap.org/data/2.5/weather?"
           f"lat={lat}&lon={lon}&units=metric&lang=ja&appid={key}")
    r = requests.get(url, timeout=10); r.raise_for_status()
    data = r.json()
    return data["weather"][0]["description"], data["main"]["temp"]

def gen_image(desc, temp, city):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    today = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    prompt = (f"Flat minimal illustration of {city} weather on {today}: "
              f"{desc}, {temp:.1f}°C, soft pastel palette, Japanese style date text.")
    res = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return res["data"][0]["url"]

def push_line(img_url, city):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"to": user_id,
            "messages": [{"type":"image",
                          "originalContentUrl": img_url,
                          "previewImageUrl": img_url,
                          "quickReply": {"items": []}},
                         ]}
    r = requests.post("https://api.line.me/v2/bot/message/push",
                      headers=headers, json=body, timeout=10)
    r.raise_for_status()
    logger.info("Pushed to LINE (%s) → %s", city, r.status_code)

def main():
    for loc in read_locations():
        desc, temp = get_weather(loc["lat"], loc["lon"])
        url = gen_image(desc, temp, loc["name"])
        push_line(url, loc["name"])

if __name__ == "__main__":
    main()
