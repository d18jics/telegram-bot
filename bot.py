from datetime import datetime
import telebot
import re

import os
from dotenv import load_dotenv
import pytz

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

USDT_RATE = 105
USDT_BALANCE = 0
ISSUED_BALANCE = 0

usdt_balance = 0
balance = 0

cur_balance = 0

# seperate command to add usdt
# initialise usdt and balance = usdt* usdt rate

def reset():
    global USDT_BALANCE
    global ISSUED_BALANCE
    global usdt_balance
    global balance
    global cur_balance

    USDT_BALANCE = 0
    ISSUED_BALANCE = 0
    usdt_balance = 0
    balance = 0
    cur_balance = 0
    return "今日入款 (0笔) \n\n今日下发 (0笔) \n\n总入款: 0 (0U)\n汇率: 105\n交易费率: 0%\n应下发: 0 | 0U\n已下发: 0 | 0U\n未下发: 0 | 0U"

def get_msg_string():
    global usdt_balance
    global balance

    # Define the IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')

    # Get the current time in IST
    ist_now = datetime.now(ist_timezone)
    ctime = ist_now.strftime("%H:%M:%S")


    cur_usdt = round(cur_balance/USDT_RATE, 2)

    usdt_balance -= cur_usdt
    balance -= cur_balance

    return f"""今日入款 (0笔) \n
今日下发 (0笔) \n
{ctime}  {cur_balance} / ({USDT_RATE}) = {cur_usdt} U \n
总入款：{cur_balance} ({cur_usdt}U)
汇率: {USDT_RATE}
交易费率: 0% \n
应下发：{cur_balance} | {cur_usdt}U
已下发：{ISSUED_BALANCE}| {USDT_BALANCE}U
未下发：-{balance} | -{round(usdt_balance,2)}U"""

@bot.message_handler(regexp=r'^\+(\d+)')
def usdt_logic(message):
    global cur_balance

    if message.text == "+0":
        bot.send_message(message.chat.id, reset())

    else:
        # Extract the digits after the '+' symbol and convert them to an integer
        cur_balance = int(message.text.replace('+', ""))
        bot.send_message(message.chat.id, get_msg_string())

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, "机器人已激活,当前默认USDT 汇率为1,默认费率为0%,您可 以通过命令修改。")

# initialise bot with usdt balance
@bot.message_handler(regexp=r'设置汇率\d+')
def set_exchange_rate(message):
    global USDT_RATE
    # Extract the digits after the '+' symbol and convert them to an integer
    USDT_RATE = int(message.text.replace('设置汇率', ''))
    bot.send_message(message.chat.id, f"汇率设置成功,当前汇率为: {USDT_RATE}")

@bot.message_handler(regexp=r'下发(\d+)u')
def set_usdt(message):
    global USDT_BALANCE
    global ISSUED_BALANCE
    global usdt_balance
    global balance

    # Define the regex pattern with a capturing group for the digits
    pattern = r'下发(\d+)u'

    # Search for the pattern in the text
    match = re.search(pattern, message.text)

    # Check if a match is found and extract the digits
    if match:
        USDT_BALANCE = int(match.group(1))
        ISSUED_BALANCE = round(USDT_BALANCE * USDT_RATE, 2)
        usdt_balance = USDT_BALANCE
        balance = ISSUED_BALANCE

        current_time = datetime.now()

        # Format the time to include only hours, minutes, and seconds
        ctime = current_time.strftime("%H:%M:%S")

        bot.send_message(message.chat.id, f"""今日入款 (0笔) \n
今日下发 (0笔) \n
{ctime}  {USDT_BALANCE}U ({round(USDT_BALANCE*USDT_RATE,2)}) DP \n
总入款：0 (0U)
汇率: {USDT_RATE}
交易费率: 0% \n
应下发：0 | 0U
已下发：{ISSUED_BALANCE}| {USDT_BALANCE}U
未下发：-{ISSUED_BALANCE} | -{USDT_BALANCE}U""")

bot.infinity_polling()