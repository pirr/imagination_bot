# -*- coding: utf-8 -*-
import sqlite3


class DB:

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()



