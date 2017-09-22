# -*- coding: utf-8 -*-
import config
import logging
import telebot
import sys
import re
import json
from subprocess import Popen, PIPE
from time import sleep
from room import Room


bot = telebot.TeleBot(config.token)
imagi_room = Room


@bot.message_handler(commands=['start'])
def start(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add('Новая комната', 'Выбрать существующую комнату')
    selected = bot.send_message(message.chat.id, 'Начнем?', reply_markup=kb)
    bot.register_next_step_handler(selected, get_select)


def get_select(message):
    if message.text == 'Новая комната':
        new_room(message)

    elif message.text == 'Выбрать существующую комнату':
        for room, items in imagi_room.get_rooms():
            print(room, items)

def new_room(message):
    imagi_room.new(chat_id=message.chat.id)
    print(imagi_room.__cash__)
    # bot.send_message(message.chat.id, 'Room {} created'.format(message.chat.id))
    photo = bot.send_message(message.chat.id, 'Отправьте фото с подписью')
    bot.register_next_step_handler(photo, add_master_photo)


def add_master_photo(message):

    if message.content_type != 'photo':
        bot.send_message(message.chat.id, 'Это не фото!')
        new_room(message)

    elif not message.caption.strip():
        bot.send_message(message.chat.id, 'Подпись та забыли!')
        new_room(message)

    else:
        print('test photo_id', message.photo[-1].file_id)
        print('test photo_caption', message.caption)
        imagi_room.add_master_photo(message.chat.id, message.photo[-1].file_id, message.caption)
        print(imagi_room.__cash__)


def test(message):
    # print('test', message)
    print('test photo_id', message.photo[-1].file_id)
    print('test photo_caption', message.caption)



def processPhotoMessage(message):

    caption = message.caption
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    print('message.caption =', caption)
    return fileID, caption



def run_game(chat_id):
    status = None
    while not status:
        status = get_from_cash(chat_id)
        sleep(1)


# @bot.message_handler(content_types=['photo'])
# def photo(message):
#     try:
#         # file_id, caption = processPhotoMessage(message)
#         return processPhotoMessage(message)
#         # file = bot.get_file(file_id)
#         # print(file)
#         # print(caption)
#         # cash_updater(message.chat.id, photo_id=file_id)
#         # run_game(message.chat.id)
#     except Exception as e:
#         print(e)
#         print('Photo not sending')



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