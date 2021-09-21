from StockDBHelper import DBHelper
import logging
import os
from random import randint
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
import pathlib
import requests
from bs4 import BeautifulSoup

db = DBHelper()
TOKEN = '1652839470:AAHwkUcB-5-_eLITVWYRvauhTEr_PgIXNrE'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)
appname = "https://stockpricebot.herokuapp.com/"
commandslist = ["/getprice", "/startupdates","/stopupdates","/settimer"]

startmessage = "Type /getprice to get current stock price. The other functions don't work yet."

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

availablePorts = ["443","80","88","8443"]
PORT = int(os.environ.get('PORT', '88'))

bot = Bot(TOKEN)

ziweiid = 245334087

gmeurl = "https://ca.finance.yahoo.com/quote/GME?p=GME&.tsrc=fin-srch"


def start(update, context):
    chatid = update.message.chat_id
    bot.send_message(chat_id = chatid, text = startmessage, reply_markup = createKeyboard())
    
def getPrice(update, context):
    chatid = update.message.chat_id
    gmepage = requests.get(gmeurl)
    html = BeautifulSoup(gmepage.text, 'lxml')
    change = html.find("span", class_ = 'Trsdu(0.3s) Mstart(4px) D(ib) Fz(24px) C($positiveColor)').text
    price = html.find('span', class_ = 'C($primaryColor) Fz(24px) Fw(b)').text
    bot.send_message(chat_id = chatid, text = price, reply_markup = createKeyboard())

def reply(update, context):
    chatid = update.message.chat_id
    chatmessage = update.message.text
    bot.send_message(chat_id=chatid, text = "test", reply_markup = createKeyboard())    

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def createKeyboard():
    button_list = []
    for each in commandslist:
       button_list.append(KeyboardButton(each, callback_data = each))
    reply_markup=ReplyKeyboardMarkup(build_menu(button_list,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
    return reply_markup
    
def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
      menu.insert(0, header_buttons)
    if footer_buttons:
      menu.append(footer_buttons)
    return menu

def main():
    updater = Updater(
        TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(["start","help"], start))
    dp.add_handler(CommandHandler("getprice",getPrice))

    dp.add_handler(MessageHandler(Filters.text, reply))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    # updater.bot.set_webhook(url=settings.WEBHOOK_URL)
    updater.bot.set_webhook(appname + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()