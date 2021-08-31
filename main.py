import logging
from aiogram import Bot, Dispatcher, executor, types
from config import exchangeratesapi_key, fastforex_key
from os import getenv
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import re
from db import init_currency_db, add_list_of_currencies, \
    get_data_from_currency_bd, \
    init_timestamp_db, add_timestamp_to_db, \
    get_data_from_timestamp_db, update_timestamp_in_db
import time


logging.basicConfig(level=logging.INFO)


bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided.")


bot = Bot(token=bot_token)
dp = Dispatcher(bot)
init_timestamp_db()


def check_time_for_db_updates():
    """updates currency list db if 10 minutes passed"""
    previous_time = get_data_from_timestamp_db()
    now_time = time.time()
    if previous_time is None:
        add_timestamp_to_db(now_time)
        previous_time = get_data_from_timestamp_db()
    if abs(previous_time[0] - now_time) > 600:
        update_timestamp_in_db(now_time)
    else:
        pass


def get_current_currency_list():
    """gets exchange rates from api"""
    url = "http://api.exchangeratesapi.io/v1/latest"
    req = requests.get(url,
                       {"access_key": exchangeratesapi_key, "base": "EUR"})
    resp = req.json()
    list_of_rates = [(i, str(round(resp["rates"][i], 2)))
                     for i in resp["rates"]]
    init_currency_db(force=True)
    add_list_of_currencies(list_of_rates)


def get_data_for_exchange(get_message):
    """returns converted money"""
    url = "https://api.fastforex.io/convert"
    querystring = {"from": get_message[2],
                   "to": get_message[4],
                   "amount": float(get_message[1]),
                   "api_key": fastforex_key}
    headers = {"Accept": "application/json"}
    response = requests.request("GET",
                                url,
                                headers=headers,
                                params=querystring)
    return str(response.json()["result"][get_message[4]])


def get_data_for_graph(currency_list):
    """returns a list of dates and exchange rates"""
    url = "http://api.exchangeratesapi.io/v1/"
    start_date = datetime.now().date()
    rates = list()
    for i in range(7):
        now_date = (start_date - timedelta(days=i)).strftime('%Y-%m-%d')
        req = requests.get(url + now_date,
                           {"access_key": exchangeratesapi_key,
                            "base": currency_list[0],
                            "symbols": currency_list[1]})
        rates_dict = {"date": now_date,
                      "exchange_rate": req.json()["rates"][currency_list[1]]}
        rates.append(rates_dict)
        rates.sort(key=lambda x: x['date'])
    return rates


def building_graph(currency_list):
    """saves a picture of the graph"""
    df = pd.DataFrame(get_data_for_graph(currency_list))
    x = df['date']
    y = df['exchange_rate']
    fig = plt.figure(figsize=(15, 10))
    plt.xticks(rotation=90)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Exchange Rates', fontsize=12)
    plt.plot(x, y)
    fig.savefig('plot.png', dpi=100)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Hello!')


@dp.message_handler(commands=['list'])
async def process_list_command(message: types.Message):
    try:
        check_time_for_db_updates()
        currency_list = get_data_from_currency_bd()
    except Exception:
        await message.answer("invalid data")
        return
    await message.answer('\n'.join([f'{currency}: {value}'
                                    for currency, value in currency_list]))


@dp.message_handler(commands=['exchange'])
async def process_exchange_command(message: types.Message):
    get_message = message.text.strip().split()
    try:
        summa = get_data_for_exchange(get_message)
    except Exception:
        await message.answer("invalid data")
        return
    await message.answer(summa + get_message[4])


@dp.message_handler(commands=['history'])
async def history_graph(message):
    get_message = (re.findall(r'\w{3}/\w{3}',
                              message.text.strip()))[0].split('/')
    try:
        building_graph(get_message)
        await bot.send_photo(message.from_user.id,
                             photo=open('plot.png', 'rb'))
    except Exception:
        await message.answer(text="Не удалось получить данные")


if __name__ == '__main__':
    executor.start_polling(dp)
