# -*- coding: utf-8 -*-
import config
import telebot
from room import Room
from functools import partial

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
    photo = bot.send_message(message.chat.id, 'Отправьте фото с подписью')
    bot.register_next_step_handler(photo, add_master_photo)


def choosing_room(message):
    rooms = []
    for room_id in imagi_room.get_room_ids():
        room = imagi_room.get_room_by_id(room_id)
        rooms.append(' '.join(['/' + str(room_id), room['master_name']]))
    rooms_str = '\n'.join(rooms)
    message = bot.send_message(message.chat.id, text=rooms_str)
    bot.register_next_step_handler(message, room_selected)


def room_selected(message):
    try:
        room_id = int(message.text.replace('/', ''))
        room = imagi_room.get_room_by_id(room_id)
        photo_mess = bot.send_message(message.chat.id, text='Отправьте фото ассоциирующееся с {}'.format(room['img_mess']))
        bot.register_next_step_handler(photo_mess, partial(add_player_photo, room_id))
    except Exception as e:
        raise e


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


def add_player_photo(room_id, message):
    print('add_player_photo')
    print(room_id)
    if message.content_type == 'photo':
        user_name = ' '.join([message.chat.first_name, message.chat.last_name])
        imagi_room.add_player(room_id, message.chat.id, user_name, message.photo[-1].file_id)
        print('player photo:', message.photo[-1].file_id)
    else:
        bot.send_message(message.chat.id, 'Это не фото!')
        message.text = str(room_id)
        room_selected(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)
