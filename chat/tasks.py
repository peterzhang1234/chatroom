# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import csv
import requests
from . import consumers
import json
import asyncio

@shared_task
def execute(command, parameter, room_group_name):
    if command == '/stock':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sendData(stock(parameter), "BOT", room_group_name))
        return True
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sendData("I do not understand that parameter", "BOT", room_group_name))
    return True


from channels.layers import get_channel_layer

async def sendData(message, from_, room_group_name):
    channel_layer = get_channel_layer()
    import datetime
    currentDT = datetime.datetime.now()
    datetime = currentDT.strftime("%Y-%m-%d %H:%M:%S")
    await channel_layer.group_send(
        room_group_name,
        {
            'type': 'chat_message',
            'username': from_,
            'datetime': datetime,
            'message': message
        }
    )
    await asyncio.sleep(5)

def stock(stock_code):
    url = "https://stooq.com/q/l/?s=%s&f=sd2t2ohlcv&h&e=csv" % (stock_code)
    with requests.Session() as s:
        download = s.get(url)
        try:
            decoded_content = download.content.decode('utf-8')
        except UnicodeDecodeError:
            return "Error while parsing response"
        except Exception:
            return "Error while parsing response 2"
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        print(my_list)
        if len(my_list) < 1 or len(my_list[1]) < 3:
            return "I could not process your request"
        if my_list[1][3] == "N/D":
            return "I could not find information for %s" % (stock_code,)
        return "%s quote is $%s per share" % (my_list[1][0], my_list[1][3])