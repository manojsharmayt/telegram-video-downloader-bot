import os
import requests
import telebot
from pytube import YouTube

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def download_instagram_video(insta_url):
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://igdownloader.io",
        "referer": "https://igdownloader.io/",
        "user-agent": "Mozilla/5.0"
    }

    data = {
        "q": insta_url
    }

    try:
        res = requests.post("https://igdownloader.io/api/ajaxSearch", headers=headers, data=data)
        result = res.json()
        video_url = result["medias"][0]["url"]
        return video_url
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Send YouTube or Instagram video link to download.")

@bot.message_handler(func=lambda message: True)
def handle_video(message):
    url = message.text.strip()

    if "instagram.com" in url:
        bot.send_chat_action(message.chat.id, 'upload_video')
        video_url = download_instagram_video(url)
        if video_url:
            bot.send_video(message.chat.id, video_url)
        else:
            bot.reply_to(message, "❌ Failed to download Instagram video.")
    
    elif "youtube.com" in url or "youtu.be" in url:
        try:
            bot.send_chat_action(message.chat.id, 'upload_video')
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by("resolution").desc().first()
            filename = "ytvideo.mp4"
            stream.download(filename=filename)
            with open(filename, "rb") as f:
                bot.send_video(message.chat.id, f)
            os.remove(filename)
        except Exception as e:
            bot.reply_to(message, f"❌ YouTube Error: {str(e)}")
    else:
        bot.reply_to(message, "❗ Send a valid YouTube or Instagram link.")

bot.infinity_polling()
