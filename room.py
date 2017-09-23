# -*- coding: utf-8 -*-
from copy import deepcopy


class Room:
    __cash__ = {}

    @classmethod
    def new(cls, chat_id):
        if chat_id not in cls.__cash__:
            cls.__cash__.update({chat_id:
                {
                    chat_id: None,
                    'status': 'created',
                    'img_mess': None,
                    'master_name': None
                }
            })

    @classmethod
    def delete(cls, chat_id):
        if chat_id in cls.__cash__:
            return cls.__cash__.pop(chat_id)

    @classmethod
    def get_room_ids(cls):
        return list(cls.__cash__)

    @classmethod
    def get_room_ids_str(cls):
        return [str(room_id) for room_id in cls.get_room_ids()]


    @classmethod
    def get_room_by_id(cls, chat_id):
        return cls.__cash__[chat_id]

    @classmethod
    def empty(cls, chat_id):
        cash = deepcopy(cls.__cash__)
        cash.pop(chat_id, None)
        if cash:
            return False
        return True

    @classmethod
    def add_master_photo(cls, chat_id, photo_id, mess, master_name):
        if chat_id in cls.__cash__ and cls.__cash__[chat_id]['status'] == 'created':
            cls.__cash__[chat_id][chat_id] = {'photo_id': photo_id, 'name': master_name}
            cls.__cash__[chat_id]['img_mess'] = mess
            cls.__cash__[chat_id]['status'] = 'in_game'
            cls.__cash__[chat_id]['master_name'] = master_name
        else:
            return 'err'

    @classmethod
    def add_player(cls, chat_id, user_id, user_name, photo_id):
        cls.__cash__[chat_id][user_id] = {'name': user_name, 'photo_id': photo_id}

    # @classmethod
    # def get_ingame_rooms(cls, chat_id):
    #     for rooms

    @classmethod
    def not_in_romm(cls, chat_id):
        if not cls.empty(chat_id):
            pass
