# -*- coding: utf-8 -*-
import config
import logging
import telebot
import sys
import re
import json
from subprocess import Popen, PIPE
from time import sleep


bot = telebot.TeleBot(config.token)
CASH = {}

@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_msg(message):
    bot.send_message(message.chat.id, message.text)


def processPhotoMessage(message):

    caption = message.caption
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    print('message.caption =', caption)
    # file = bot.get_file(fileID)
    # print('file.file_path =', file.file_path)
    return fileID, caption


def run_game(chat_id):
    status = None
    while not status:
        status = get_from_cash(chat_id)
        sleep(1)


@bot.message_handler(content_types=['photo'])
def photo(message):
    try:
        file_id, caption = processPhotoMessage(message)
        # file = bot.get_file(file_id)
        # print(file)
        # print(caption)
        cash_updater(message.chat.id, photo_id=file_id, caption='oops')
        print(CASH)
        run_game(message.chat.id)
    except Exception as e:
        print(e)
        print('Photo not sending')

def cash_updater(chat_id, photo_id, caption):

    if not CASH:
        CASH[chat_id] = {chat_id: (photo_id, caption)}
    elif chat_id in CASH:
        print('Room creating')
    else:
        for chat in list(CASH):
            if len(CASH[chat]) < 2 and chat_id not in CASH[chat]:
                CASH[chat].update({chat_id: (photo_id, caption)})


def get_from_cash(chat_id):

    if chat_id in CASH:
        print('You are master')
        if len(CASH[chat_id]) > 1:
            for user_id in list(CASH[chat_id]):
                if user_id != chat_id:
                    photo_id, caption = CASH[chat_id][user_id]
                    bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)
                    return 'ok'

    else:
        for chat in list(CASH):
            if chat_id in CASH[chat]:
                print('YOU ARE PLAYER')
                for user_id in list(CASH[chat]):
                    if user_id != chat_id:
                        photo_id, caption = CASH[chat_id][user_id]
                        bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)
                        return 'ok'



if __name__ == '__main__':
    bot.polling(none_stop=True)