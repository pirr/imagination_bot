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
        choosing_room(message)


def new_room(message):
    imagi_room.new(chat_id=message.chat.id)
    # print(imagi_room.__cash__)
    # bot.send_message(message.chat.id, 'Room {} created'.format(message.chat.id))
    photo = bot.send_message(message.chat.id, 'Отправьте фото с подписью')
    bot.register_next_step_handler(photo, add_master_photo)


# @bot.inline_handler(lambda query: len(query.query) > 0)
def choosing_room(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for room_id in imagi_room.get_room_ids():
        room = imagi_room.get_room_by_id(room_id)
        keyboard.add(telebot.types.InlineKeyboardButton(text=room['master_name'], callback_data='room_' + str(room_id)))
    bot.send_message(message.chat.id, text='Выберите комнату', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: 'room_' in c.data)
def call_back_room(c):
    room_id = int(c.data.split('_')[1])
    c.message.room_id = room_id
    room = imagi_room.get_room_by_id(room_id)
    print('call back room id:', c.message.room_id)
    try:
        # bot.edit_message_text(chat_id=c.message.chat.id,
        #                       message_id=c.message.message_id,
        #                       text='Отправьте фото ассоциирующееся с "{}"'.format(room['img_mess']))
        add_player_photo(c.message)
        # print('calback photo:', photo.photo[-1].file_id)

    except Exception as e:
        print('callback error:', e)


def add_master_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, 'Это не фото!')
        new_room(message)

    elif not message.caption or not message.caption.strip():
        bot.send_message(message.chat.id, 'Подпись та забыли!')
        new_room(message)

    else:
        user_name = ' '.join([message.chat.first_name, message.chat.last_name])
        imagi_room.add_master_photo(message.chat.id,
                                    message.photo[-1].file_id,
                                    message.caption,
                                    user_name
                                    )
        # print(imagi_room.__cash__)

def add_player_photo(message):
    print('add_player_photo')
    room_id = message.room_id
    room = imagi_room.get_room_by_id(room_id)
    photo_message = bot.send_message(message.chat.id, 'Отправьте фото ассоциирующееся с "{}"'.format(room['img_mess']))

    if photo_message.content_type != 'photo':
        bot.send_message(message.chat.id, 'Это не фото!!')
        # add_player_photo(message)

    else:
        user_name = ' '.join([photo_message.chat.first_name, photo_message.chat.last_name])
        imagi_room.add_player(room_id,
                              photo_message.chat.id,
                              user_name,
                              photo_message.photo[-1].file_id
                              )
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



if __name__ == '__main__':
    bot.polling(none_stop=True)
