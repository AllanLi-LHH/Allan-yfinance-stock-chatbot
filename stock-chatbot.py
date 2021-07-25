from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
import re
import numpy as np
import telegram
import yfinance as yf
import pandas as pd
import time
import matplotlib.pyplot as plt
import pylab as pl
from PIL import Image, ImageDraw, ImageFont
import random, string, threading
from typing import Dict
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

trainer = Trainer(config.load("config_spacy.yml"))
training_data = load_data('stock.json')
interpreter = trainer.train(training_data)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

bot_name = 'LHH-stock-bot'
bot = telegram.Bot(token = '<Your-api-token>')
bot.sendMessage(chat_id = <Your chat id>, text = "Hello,I'm {}.You can ask me any question about stock!".format(bot_name))

updater = Updater(token = '<Your-api-token>', use_context = True)
dispatcher = updater.dispatcher

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['Age', 'Name'],
    ['Country', 'Something else...'],
    ['Done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard = True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        "Hi! I am chatter_bot. I will hold a simple conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup = markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY


def custom_choice(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup = markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup = ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END



conv_handler = ConversationHandler(
    entry_points = [MessageHandler(Filters.text & ~Filters.command, start)],
    states = {
        CHOOSING: [
            MessageHandler(
                Filters.regex('^(Age|Name|Country)$'), regular_choice
            ),
            MessageHandler(Filters.regex('^Something else...$'), custom_choice),
        ],
        TYPING_CHOICE: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
            )
        ],
        TYPING_REPLY: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                received_information,
            )
        ],
    },
    fallbacks = [MessageHandler(Filters.regex('^Done$'), done)],
)


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)


def random_xy(img):
    x = random.randint(0, img.size[0])
    y = random.randint(0, img.size[1])
    return (x, y)


def Vertification_Code_Generator(bot):
    str01 = ''

    img = Image.new('RGB', (640, 160), color = (0, 0, 0))
    canvas = ImageDraw.Draw(img)
    font = ImageFont.FreeTypeFont('arial.ttf', size = 128)
    for x in range(0, img.size[0]):
        for y in range(0, img.size[1]):
            canvas.point((x, y), fill = random_color())
    for i in range(4):
        str02 = random.choice(string.ascii_letters + string.digits)
        str01 += str02
        canvas.text((i * 160, 0), str02, font = font, fill = random_color())
        for j in range(15):
            canvas.line((random_xy(img), random_xy(img)), fill = random_color(), width = 2)
    img.save("pictures/verticode.png")
    bot.sendPhoto(chat_id = 1141038444, photo = open('pictures/verticode.png', 'rb'))
    return str01.lower()


str00 = Vertification_Code_Generator(bot)
Now_time = str(time.strftime("%b %d %Y %H:%M:%S", time.localtime()))

intent_responses = {
    "greet": ["Hi",
              "Hello",
              "Howdy",
              'hey',
              "Hi there",
              'Hi,nice to see you',
              'Hello, nice to see you',
              'Hey,long time no see'],
    'affirm': ["It's my pleasure to help you:)",
               'So smart I am:)',
               'Any other question then?',
               'glad to help you!',
               'please be free to ask me!',
               '',
               ':)',
               'Happy to have helped you:)'],
    'goodbye': ['Bye',
                'Bye bye',
                'See you',
                'See you next time',
                "Good Bye",
                'I will be seeing you'],
    'name_query': ['My name is {}'.format(bot_name),
                   'They call me {}'.format(bot_name),
                   'You can call me {}'.format(bot_name),
                   'I am {}'.format(bot_name),
                   'I would like you can call me {}'.format(bot_name)],
    'time_query': ['Today is ' + Now_time,
                   'The time is ' + Now_time,
                   'Today is ' + Now_time
                   ],

}

pattern_list = ["I'd like to know (.*)",
                "Could you tell me (.*)",
                "Could you please tell me (.*)",
                "Do you know (.*)",
                "I wonder (.*)",
                "How about (.*)",
                "What's (.*)",
                "I want to know about (.*)",
                "I want to know something about (.*)",
                "What was (.*)"]


def get_info(message):

    data = interpreter.parse(message)
    intent = data["intent"]["name"]  # 获取意图
    entities = data["entities"]  # 获取实体
    org_list=[]
    entity_dic = {}  # 存放消息实体
    for ent in entities:
        if ent["entity"] == 'org':
            org_list.append(str(ent["value"]))
        else:
            entity_dic[ent["entity"]] = str(ent["value"]).replace(' ', '')

    return intent, org_list, entity_dic


handlable_intent = ['highest_price_query', 'lowest_price_query', 'price_query', 'volume_query', 'stock_query']
precise_intent = ['highest_price_query', 'lowest_price_query', 'price_query', 'volume_query']


start_date = None
end_date = None
period = None
intent = None
entities = {}
org_list = []
chat_id = None

bar_color = ['red', 'yellow', 'blue', 'green', 'coral', 'orange', 'pink']
paint_color = ['r', 'y', '', 'b', 'g', 'c', 'm', 'k']
dot_style = ['-o', '--o', '-.o', '-d', '-.s']


def formattime(t):
    array = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    return time.strftime("%Y-%m-%d", array)


def querydate(org, cur_start_date, cur_end_date, index):
    result = ''
    global entities
    global intent
    global org_list
    global start_date
    global end_date
    global graph_class
    plt.cla()
    flag = None
    # 可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        item = item.upper()
        result += item + ':\n'
        data = yf.download(item, start = cur_start_date, end = cur_end_date)
        flag = data.empty
        if flag:
            result += 'Sorry,the stock market is CLOSED during the appointed period!\n\n'
        else:
            data_set = data[index]
            data_len = len(data_set)
            if index == 'Close':
                result += 'Date               ' + 'Price' + '\n'
            else:
                result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date = formattime(str(data_set.index[i]))  # date为str类型
                value = '%.6f' % data_set.values[i]  # value为str类型
                result += date + '   ' + value + '\n'
                date_list.append(date)
                value = float(value)
                value_list.append(value)
            plt.plot(date_list, value_list, paint_color[seq] + dot_style[seq], label = item)
        result += "\n"
    if flag == False:
        result += "And I'll draw you a graph to illustrate the trend of change more clearly. "
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.sendMessage(chat_id = chat_id, text = result, reply_markup = reply_markup)
    if flag == False:
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Quantity', fontsize = 14)
        plt.legend(loc = "best")
        pl.xticks(rotation = 75)
        now_time = str(int(time.time()))
        plt.savefig("pictures/" + now_time + '.png', dpi = 200, bbox_inches = 'tight')
        bot.sendPhoto(chat_id = chat_id, photo = open('pictures/' + now_time + '.png', 'rb'))
        entities = {}
        intent = None
        org_list = []
        start_date = None
        end_date = None
        graph_class = 0


def bar_querydate(org, cur_start_date, cur_end_date, index):
    result = ''
    global graph_class
    global entities
    global intent
    global org_list
    global start_date
    global end_date
    global period
    plt.cla()
    flag = None
    index1 = np.arange(0)
    list1 = [0]
    # 可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        item = item.upper()
        result += item + ':\n'
        data = yf.download(item, start = cur_start_date, end = cur_end_date)  # data为DataFrame类型
        flag = data.empty
        if flag:
            result += 'Sorry,the stock market is CLOSED during the appointed period!\n\n'
        else:
            data_set = data[index]
            data_len = len(data_set)
            index1 = np.arange(data_len)
            if index == 'Close':
                result += 'Date               ' + 'Price' + '\n'
            else:
                result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date = formattime(str(data_set.index[i]))  # date为str类型
                value = '%.6f' % data_set.values[i]  # value为str类型
                result += date + '   ' + value + '\n'
                date_list.append(date)
                value = float(value)
                value_list.append(value)
            list1 = date_list
            plt.bar(index1+0.2*seq, value_list, width = 0.2, color = bar_color[seq], label = item)
    result += "\n"

    result += "And I'll draw you a graph to illustrate the trend of change more clearly. "
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.sendMessage(chat_id = chat_id, text = result, reply_markup = reply_markup)
    if flag == False:
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Quantity', fontsize = 14)
        plt.legend(loc = "best")
        plt.xticks(index1, list1)
        pl.xticks(rotation = 75)
        now_time = str(int(time.time()))
        plt.savefig("pictures/" + now_time + '.png', dpi = 200, bbox_inches = 'tight')
        bot.sendPhoto(chat_id = chat_id, photo = open('pictures/' + now_time + '.png', 'rb'))
        entities = {}
        intent = None
        org_list = []
        start_date = None
        end_date = None
        graph_class = 0


def queryperiod(org, cur_period, index):
    global entities
    global intent
    global org_list
    global period
    global graph_class
    result = ''
    plt.cla()
    flag = None
    index1 = np.arange(0)
    list1 = [0]
    # 可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        item = item.upper()
        result += item + ':\n'
        data = yf.download(item, period = cur_period)
        flag = data.empty
        if flag:
            result += 'Sorry,the stock market is CLOSED during the appointed period!\n\n'
        else:
            data_set = data[index]
            data_len = len(data_set)
            index1 = np.arange(data_len)
            if index == 'Close':
                result += 'Date               ' + 'Price' + '\n'
            else:
                result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date = formattime(str(data_set.index[i]))
                value = '%.6f' % data_set.values[i]
                result += date + '   ' + value + '\n'
                date_list.append(date)
                value = float(value)
                value_list.append(value)
            list1 = date_list
            plt.plot(date_list, value_list, paint_color[seq] + dot_style[seq], label = item)
    result += "\n"
    result += "And I'll draw you a graph to illustrate the trend of change more clearly. "
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.sendMessage(chat_id = chat_id, text = result, reply_markup = reply_markup)
    if flag == False:
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Quantity', fontsize = 14)
        plt.legend(loc = "best")
        plt.xticks(index1, list1)
        pl.xticks(rotation = 75)
        now_time = str(int(time.time()))
        plt.savefig("pictures/" + now_time + '.png', dpi = 200, bbox_inches = 'tight')
        bot.sendPhoto(chat_id = chat_id, photo = open('pictures/' + now_time + '.png', 'rb'))
        entities = {}
        intent = None
        org_list = []
        graph_class = 0
        period = None


def bar_queryperiod(org, cur_period, index):
    global graph_class
    global entities
    global intent
    global org_list
    global period
    result = ''
    global graph_class
    global entities
    global intent
    global org_list
    global start_date
    plt.cla()
    flag = None
    index1 = np.arange(0)
    list1 = [0]
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        item = item.upper()
        result += item + ':\n'
        data = yf.download(item, period = cur_period)
        flag = data.empty
        if flag:
            result += 'Sorry,the stock market is CLOSED during the appointed period!\n\n'
        else:
            data_set = data[index]
            data_len = len(data_set)
            index1 = np.arange(data_len)
            if index == 'Close':
                result += 'Date               ' + 'Price' + '\n'
            else:
                result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date = formattime(str(data_set.index[i]))  # date为str类型
                value = '%.6f' % data_set.values[i]  # value为str类型
                result += date + '   ' + value + '\n'
                date_list.append(date)
                value = float(value)
                value_list.append(value)
            list1 = date_list
            plt.bar(index1 + 0.2 * seq, value_list, width = 0.2, color = bar_color[seq], label = item)

    result += "\n"

    result += "And I'll draw you a graph to illustrate the trend of change more clearly. "
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.sendMessage(chat_id = chat_id, text = result, reply_markup = reply_markup)
    if flag == False:
        plt.xlabel('Date', fontsize = 14)
        plt.ylabel('Quantity', fontsize = 14)
        plt.legend(loc = "best")
        plt.xticks(index1, list1)
        pl.xticks(rotation = 75)
        now_time = str(int(time.time()))
        plt.savefig("pictures/" + now_time + '.png', dpi = 200, bbox_inches = 'tight')
        bot.sendPhoto(chat_id = chat_id, photo = open('pictures/' + now_time + '.png', 'rb'))
        entities = {}
        intent = None
        org_list = []
        start_date = None
        graph_class = 0
        period = None




def highest_price_query(org, start_date, end_date, period):
    if start_date != None and graph_class == 1:
        querydate(org, start_date, end_date, 'High')
    elif start_date != None and graph_class == 2:
        bar_querydate(org, start_date, end_date, 'High')

    elif graph_class == 1:
        queryperiod(org, period, 'High')
    else:
        bar_queryperiod(org, period, 'High')


def lowest_price_query(org, start_date, end_date, period):
    if start_date != None and graph_class == 1:
        querydate(org, start_date, end_date, 'Low')
    elif start_date != None and graph_class == 2:
        bar_querydate(org, start_date, end_date, 'Low')

    elif graph_class == 1:
        queryperiod(org, period, 'Low')
    else:
        bar_queryperiod(org, period, 'Low')


def price_query(org, start_date, end_date, period):
    if start_date != None and graph_class == 1:
        querydate(org, start_date, end_date, 'Close')
    elif start_date != None and graph_class == 2:
        bar_querydate(org, start_date, end_date, 'Close')

    elif graph_class == 1:
        queryperiod(org, period, 'Close')
    else:
        bar_queryperiod(org, period, 'Close')


def volume_query(org, start_date, end_date, period):
    if start_date != None and graph_class == 1:
        querydate(org, start_date, end_date, 'Volume')
    elif start_date != None and graph_class == 2:
        bar_querydate(org, start_date, end_date, 'Volume')

    elif graph_class == 1:
        queryperiod(org, period, 'Volume')
    else:
        bar_queryperiod(org, period, 'Volume')


def formatdate(date):
    beforeArray = time.strptime(date, "%Y-%m-%d")
    timeStamp = int(time.mktime(beforeArray))
    timeStamp += 24 * 60 * 60
    afterArray = time.localtime(timeStamp)  # 时间戳转结构化时间
    return time.strftime("%Y-%m-%d", afterArray)



def handle(cur_intent, cur_org_list, cur_entities):  # slot filling
    global start_date
    global end_date
    global period
    global intent
    global entities
    global org_list
    global start_date
    global end_date
    global chat_id
    global period
    if cur_intent in handlable_intent:
        if len(org_list) != 0 and entities != {}:
            intent = cur_intent

        elif intent in precise_intent and cur_intent =='stock_query' :
            if start_date != None:       # laking the name of stock
                org_list = cur_org_list[:]
            else:
                entities = cur_entities.copy()
                org_list = cur_org_list[:]
                start_date = None
                end_date = None
                period = None

        elif cur_intent in precise_intent:
            intent = cur_intent
            entities = cur_entities.copy()
            org_list = cur_org_list[:]
            start_date = None
            end_date = None
            period = None

        elif cur_intent != 'stock_query':
            intent = cur_intent
            entities = cur_entities.copy()
            org_list = cur_org_list[:]
            start_date = None
            end_date = None
            period = None
        elif cur_intent == 'stock_query':
            intent = cur_intent
            org_list = cur_org_list[:]

        else:
            entities = cur_entities.copy()
            org_list = cur_org_list[:]
            start_date = None
            end_date = None
            period = None


    else:
        if intent in handlable_intent:
            for item in cur_org_list:
                org_list.append(item)
            for key, value in cur_entities.items():
                entities[key] = str(value).replace(' ', '')
        else:
            intent = cur_intent


    for key, value in entities.items():
        if key == 'start_date':
            start_date = value
        elif key == 'end_date':
            end_date = value
        elif key == 'period':
            period = value

    if len(org_list) == 0 and (start_date != None or period != None or intent in precise_intent): # start_date和period二选一即可
        bot.sendMessage(chat_id = chat_id, text = "So which stock do you want to ask about?")
    elif len(org_list) == 0 and (start_date == None and end_date ==None and period == None):
        bot.sendMessage(chat_id = chat_id, text = "Sorry! I cannot decipher your intention")

    elif len(org_list) != 0 and (start_date == None and period == None):
        custom_keyboard = [['1 day', '5 days', '1 month', '3 months']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(chat_id = chat_id, text = "Then for which period do you want to ask ?",
                        reply_markup = reply_markup)
    elif len(org_list) != 0 and  (period != None and intent not in precise_intent):
        custom_keyboard2 = [['highest_price', 'lowest_price', 'price', 'volume']]
        reply_markup2 = telegram.ReplyKeyboardMarkup(custom_keyboard2)
        bot.sendMessage(chat_id = chat_id, text = "Which kinds of stock information do you want to know?", reply_markup = reply_markup2)
    elif len(org_list) != 0 and (period != None or (start_date !=None and end_date != None)) and intent in precise_intent and graph_class == 0:
        custom_keyboard3 = [['Line chart', 'Bar chart']]
        reply_markup3 = telegram.ReplyKeyboardMarkup(custom_keyboard3)
        bot.sendMessage(chat_id = chat_id, text = "Which kind of chart do you like ?",
                        reply_markup = reply_markup3)

    else:
        if start_date != None:
            start_date = start_date.replace(" ", "")
            start_date = formatdate(start_date)
            end_date = end_date.replace(" ", "")
            end_date = formatdate(end_date)
        if intent == 'highest_price_query':
            highest_price_query(org_list, start_date, end_date, period)
        elif intent == 'lowest_price_query':
            lowest_price_query(org_list, start_date, end_date, period)
        elif intent == 'price_query':
            price_query(org_list, start_date, end_date, period)
        elif intent == 'volume_query':
            volume_query(org_list, start_date, end_date, period)


verifying_flag = 1  # Verification code function switch
chatter_flag = -99  # Small talk mode switch
graph_class = 0

def chat(update, context):
    global intent
    global entities
    global org_list
    global start_date
    global end_date
    global chat_id
    global period
    global str00
    global verifying_flag
    global chatter_flag
    global graph_class

    chat_id = 1141038444
    message = update.message.text
    if verifying_flag  == 1:
        if message.lower() != str00:
            context.bot.send_message(chat_id = update.effective_chat.id, text = 'Wrong verification code input, please try again!')
            str00 = Vertification_Code_Generator(bot)
            return 0
        else:
            context.bot.sendMessage(chat_id = chat_id, text = "All right, now you can ask me some questions!")
            verifying_flag  = 0
            return 0

    for item in pattern_list:
        match = re.search(item, message, re.I)
        if match is not None:
            message = match.group(1)
            break
    if message == "Line chart":
        graph_class = 1
        handle(intent, org_list, entities)
    elif message == "Bar chart":
        graph_class = 2
        handle(intent, org_list, entities)
    else:
        cur_intent, cur_org_list, cur_entities = get_info(message)  # get intent, entities...

        if cur_intent == 'greet' or cur_intent == 'affirm' or cur_intent == 'goodbye' or cur_intent == 'name_query' or cur_intent == 'time_query':
            chatter_flag += 1
            context.bot.sendMessage(chat_id = chat_id, text = random.choice(intent_responses[cur_intent]))
        else:

            handle(cur_intent, cur_org_list, cur_entities)  # handle the analytical results
        if chatter_flag > 8:  
            context.bot.send_message(chat_id = update.effective_chat.id,
                                     text = 'switch to High-LEVEL conversation model, please wait about 10 seconds..........')
            t = threading.Thread(target = second_thread(bot))
            t.start()
            updater.stop()


def second_thread(bot):
    time.sleep(10)
    bot.sendMessage(chat_id = <Your chat id>, text = "Done!")
    updater2 = Updater(token = '<Your-api-token>', use_context = True)
    dispatcher2 = updater2.dispatcher
    dispatcher2.add_handler(conv_handler)
    updater2.start_polling()


dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))
updater.start_polling()
