#!/usr/bin/python

# Copyright (c) 2017
# Author: Ray Stojonic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ConfigParser
import logging
import logging.config
import time

import sqlite3


class HumidifierDAO():

    CONFIG_SECTION = 'HumidifierDAO_Options'

    def __init__(self, config):
        self.logger = logging.getLogger('HumidifierDao')
        self.db_file = config.get(HumidifierDAO.CONFIG_SECTION, 'db_fullpath')

    def insert_humid_mode(self, mode):
        ''' Insert new humidifier mode into database.
            The time of the insertion will be used as the [created] field.
        '''

        insert = ''' insert into humidifier(created, mode)
                     values(datetime('now', 'localtime'), ?); '''

        try:
            conn = self.get_connection()
            with conn:
                cur = conn.cursor()
                cur.execute(insert, (mode,))
                return cur.lastrowid

        except Exception as e:
            self.logger.error(e)

        finally:
            conn.close()
    
    def select_range(self, begin, end):
        ''' Return readings from provided time range.
            begin: datetime string of format %Y-%m-%d %H:%M(:%S)
            end  : datetime string of format %Y-%m-%d %H:%M(:%S)
        '''

        sql = """ select created, mode 
                  from humidifier
                  where created > ?
                      and created < ?; """
    
        self.logger.debug(sql.replace('?', '{}').format(begin, end))

        try:
            conn = self.get_connection()
            with conn:
                cur = conn.cursor()
                cur.execute(sql, (begin, end))
                data = cur.fetchall()
                return data

        except Exception as e:
            self.logger.error(e)

        finally:
            conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_file)
