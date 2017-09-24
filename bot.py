# -*- coding: utf-8 -*-
import config
import telebot
from room import Room
from functools import partial
from random import shuffle


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
    try:
        rooms = []
        for room_id in imagi_room.get_room_ids():
            room = imagi_room.get_room_by_id(room_id)
            if room['status'] == 'wait':
                rooms.append(' '.join(['/' + str(room_id), room['master_name']]))
        rooms_str = '\n'.join(rooms)
        print(rooms_str)
        message = bot.send_message(message.chat.id, text=rooms_str)
        bot.register_next_step_handler(message, room_selected)
    except Exception as e:
        print(e)


def room_selected(message):
    try:
        room_id = int(message.text.strip('/'))
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
        bot.send_message(message.chat.id, text='Ваша игровая комната создана')


def add_player_photo(room_id, message):
    if message.content_type == 'photo':
        user_name = ' '.join([message.chat.first_name, message.chat.last_name])
        imagi_room.add_player(room_id, message.chat.id, user_name, message.photo[-1].file_id)
        if len(imagi_room.get_room_by_id(room_id)['players']) > 0:
            in_game(room_id, user_name)

    else:
        bot.send_message(message.chat.id, 'Это не фото!')
        message.text = str(room_id)
        room_selected(message)


def in_game(room_id, user_name):
    message = bot.send_message(room_id, text='В Вашу игровую зашел {} начать игру?/{}'.format(user_name, room_id))
    bot.register_next_step_handler(message, partial(run_game, room_id))


def run_game(room_id, message):
    if message.text.strip('/') == str(room_id):
        imagi_room.change_status(room_id, 'in_game')
        room = imagi_room.get_room_by_id(room_id)
        photo_ids = [room['master_photo_id']] + [room['players'][player_id]['photo_id'] for player_id in list(room['players'])]
        shuffle(photo_ids)
        for chat_id in list(room['players']):
            bot.send_message(chat_id, text='Игра началась')
            for photo_id in photo_ids:
                bot.send_photo(chat_id, photo=photo_id, caption='/'+photo_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
