import telebot
import requests
import logging

logger = telebot.logger

from dotenv import dotenv_values

config = dotenv_values(".env")

bot = telebot.TeleBot(config["BOT_TOKEN"])

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
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
    payload = {'apikey': config["OCR_API_KEY"],
                'isOverlayRequired': False,
                'language': 'eng'
            }
    resp = requests.post(url, data=payload, files=files)
    if resp.status_code == 200:
        bot.send_message(message.chat.id, resp.json()['ParsedResults'][0]['ParsedText'])

bot.polling()