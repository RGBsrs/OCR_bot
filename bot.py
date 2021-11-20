import telebot
import logging
import os

from telebot import types
from flask import Flask, request

from services import OcrAPI

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OCR_API_KEY = os.environ.get("OCR_API_KEY")
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")


logger = telebot.logger

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
api = OcrAPI(api_key=OCR_API_KEY)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, 'Ready to OCR')

    # markup = types.ReplyKeyboardMarkup(row_width=3)
    # itembtn1 = types.KeyboardButton('EN')
    # itembtn2 = types.KeyboardButton('RU')
    # itembtn3 = types.KeyboardButton('DE')
    # markup.add(itembtn1, itembtn2, itembtn3)
    # bot.send_message(message.chat.id, "Choose language:", reply_markup=markup)

    # markup = types.ReplyKeyboardRemove(selective=False)
    # bot.send_message(message.chat.id, 'Processing', reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def choose_image_language(message):
    photo_id = message.photo[-1].file_id
    photo = bot.get_file(photo_id)
    downloaded_file = bot.download_file(photo.file_path)

    f = open('test_image.jpg', 'wb')
    f.write(downloaded_file)
    f.close()
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('eng', 'rus', 'ger')
    msg = bot.send_message(message.chat.id, "Choose OCR language:", reply_markup=markup)
    bot.register_next_step_handler(msg, ocr_image)

def ocr_image(message):
    language = message.text
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'Processing', reply_markup=markup)

    files = {'file': ('test_image.jpg', open('test_image.jpg', 'rb'))}
    payload = {
                'isOverlayRequired': False,
                'language': language
                }
    resp = api.make_request(payload, files)

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