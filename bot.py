import telebot
import requests
import logging
import os

from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OCR_API_KEY = os.environ.get("OCR_API_KEY")
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")


logger = telebot.logger

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, 'Hi')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

@bot.message_handler(content_types=['photo'])
def ocr_image(message):
    photo_id = message.photo[-1].file_id
    photo = bot.get_file(photo_id)
    downloaded_file = bot.download_file(photo.file_path)
    f = open('test_image.jpg', 'wb')
    f.write(downloaded_file)
    f.close()
    files = {'file': ('test_image.jpg', open('test_image.jpg', 'rb'))}
    url = 'https://api.ocr.space/parse/image'
    payload = {'apikey': OCR_API_KEY,
                'isOverlayRequired': False,
                'language': 'eng'
            }
    resp = requests.post(url, data=payload, files=files)
    if resp.status_code == 200:
        bot.send_message(message.chat.id, resp.json()['ParsedResults'][0]['ParsedText'])

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'https://{HEROKU_APP_NAME}.herokuapp.com/' + BOT_TOKEN)
    return "!", 200

if __name__ == "__main__":
    app.run()