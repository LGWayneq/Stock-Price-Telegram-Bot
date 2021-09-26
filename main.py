from StockDBHelper import DBHelper
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
import urllib.request
import json
import datetime

db = DBHelper()
TOKEN = '1652839470:AAHwkUcB-5-_eLITVWYRvauhTEr_PgIXNrE'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)
bot = Bot(TOKEN)
#appname = "https://stockpricebot.herokuapp.com/"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#availablePorts = ["443","80","88","8443"]
#PORT = int(os.environ.get('PORT', '443'))

commandslist = ["/getprice", "/setalerts"]
with open("startmessage.txt", "r") as startfile:
    startmessage = startfile.read()
    startfile.close()
baseurl = "https://query1.finance.yahoo.com/v8/finance/chart/{}?region=SG&lang=en-SG&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=sg.finance.yahoo.com&.tsrc=finance"

def start(update, context):
    chatid = update.message.chat_id
    bot.send_message(chat_id = chatid, text = startmessage, reply_markup = createKeyboard(commandslist))

def get_price_start(update,context):
    chatid = update.message.chat_id
    pasttickers = db.getPastTickers(chatid)
    bot.send_message(chat_id = chatid, text = "Select one of your past three tickers, or input desired ticker\nType /cancel to cancel.", reply_markup = createKeyboard(pasttickers))
    return 1

def set_ticker(update, context):
    chatid = update.message.chat_id
    ticker = update.message.text
    if ticker == "/cancel":
        return get_price_cancel(update,context)
    try:
        response = urllib.request.urlopen(baseurl.format(ticker))
        price = json.load(response)["chart"]["result"][0]["meta"]["regularMarketPrice"]    
        db.updatePastTickers(chatid, ticker.upper())
        bot.send_message(chat_id = chatid, text = price, reply_markup = createKeyboard(commandslist))
    except:
        bot.send_message(chat_id = chatid, text = "Ticker does not exist", reply_markup = createKeyboard(commandslist))
    return ConversationHandler.END

def get_price_cancel(update,context):
    chatid = update.message.chat_id
    bot.send_message(chat_id = chatid, text = "Cancelled /getprice call", reply_markup = createKeyboard(commandslist))
    return ConversationHandler.END

def set_alert_start(update, context):
    chatid = update.message.chat_id
    bot.send_message(chat_id = chatid, text = "Select On to turn on hourly alerts\nSelect Off to turn off hourly alerts\nSelect Cancel to cancel selection", reply_markup = createKeyboard(['On','Off','Cancel']))
    return 1
    
def set_alert_main(update, context):
    chatid = update.message.chat_id
    choice = update.message.text
    if choice == "On":
        db.setAlerts(chatid, True)
        bot.send_message(chat_id = chatid, text = "Alerts set to On", reply_markup = createKeyboard(commandslist))
    elif choice == "Off":
        db.setAlerts(chatid, False)
        bot.send_message(chat_id = chatid, text = "Alerts set to Off", reply_markup = createKeyboard(commandslist))
    elif choice == "Cancel":
        bot.send_message(chat_id = chatid, text = "Alerts choice selection cancelled", reply_markup = createKeyboard(commandslist))
    return ConversationHandler.END
        
def set_alert_fallback(update, context):
    chatid = update.message.chat_id
    choice = update.message.text
    bot.send_message(chat_id = chatid, text = "Choice of '{}' does not exist. Please try again.".format(choice), reply_markup = createKeyboard(['On','Off','Cancel']))
    return 1    

def set_alert_cancel(update, context):
    chatid = update.message.chat_id
    alert_status = db.checkAlerts(chatid)
    if alert_status == 1:
        alert_status = True
    else:
        alert_status = False
    bot.send_message(chat_id = chatid, text = "Set alert cancelled.\nAlerts will remain as {}".format(alert_status), reply_markup = createKeyboard(commandslist))
    return ConversationHandler.END

def alert_daily(context: CallbackContext):
    user_list = db.getAllAlerts()
    for user in user_list:
        ticker_list = db.getPastTickers(user)
        full_message = ""
        for ticker in ticker_list:
            response = urllib.request.urlopen(baseurl.format(ticker))
            price = json.load(response)["chart"]["result"][0]["meta"]["regularMarketPrice"]    
            full_message = full_message + "{}:  {}\n".format(ticker, price)
        bot.send_message(chat_id = user, text = full_message ,reply_markup = createKeyboard(commandslist))
    

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def createKeyboard(keylist):
    button_list = []
    for each in keylist:
        if each == None:
            continue
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
    db.createTable()
    updater = Updater(
        TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    job = updater.job_queue

    dp.add_handler(CommandHandler(["start","help"], start))
    
    setAlertConvHandler = ConversationHandler(
        entry_points=[CommandHandler('setalerts', set_alert_start)],
        states = {1: [MessageHandler(Filters.regex(r'^(On|Off|Cancel)?'), set_alert_main)]},
        fallbacks = [CommandHandler('cancel', set_alert_cancel),
                     MessageHandler(Filters.text, set_alert_fallback)]
    )
    
    getPriceConvHandler = ConversationHandler(
        entry_points=[CommandHandler('getprice', get_price_start)],
        states = {1: [MessageHandler(Filters.text, set_ticker)]},
        fallbacks = [CommandHandler('cancel', get_price_cancel)]
    )
    
    dp.add_handler(getPriceConvHandler)
    dp.add_handler(setAlertConvHandler)
    
    job.run_daily(alert_daily, days = (0,1,2,3,4), time = datetime.time(hour = 13, minute = 30, second = 10)) #alert for market, time in UTC+0
    job.run_daily(alert_daily, days = (0,1,2,3,4), time = datetime.time(hour = 19, minute = 30, second = 10))  #alert for market close, time in UTC+0
    
    # log all errors
    dp.add_error_handler(error)
    
    updater.start_polling()
    
    # Start the Bot
    """updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    
    updater.bot.set_webhook(appname + TOKEN)"""

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()