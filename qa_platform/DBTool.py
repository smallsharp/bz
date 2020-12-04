# -*- coding: utf-8 -*-

import sys
import pymysql
import re


# 简单起见，不做任何参数检查或者异常处理

class DBTool:

    def __init__(self, db_config=None, database=None):

        if database:
            db_config['database'] = database
        db_config['cursorclass'] = pymysql.cursors.DictCursor
        self.cnx = pymysql.connect(**db_config)

    def _get_cnx(self):
        if self.cnx.open:
            return self.cnx
        else:
            self.cnx.ping(reconnect=True)
            return self.cnx

    def s(self, table, select=None, where=None, order=None, **ignore):
        param_list = []
        q_table = table

        q_select = ' * '
        if select:
            q_select = ' , '.join(select)

        q_where = ''
        if where:
            cols = []
            for k, v in where.items():
                cols.append(k + '=%s')
                param_list.append(v)
            q_where = ' WHERE ' + ' AND '.join(cols)

        q_order = ''
        if order:
            q_order = ' ORDER BY ' + ' , '.join([i[0] + ' ' + i[1] for i in order])

        sql = 'SELECT ' + q_select + ' FROM ' + q_table + q_where + q_order
        cnx = self._get_cnx()
        cursor = cnx.cursor()
        cursor.execute(sql, param_list)
        ret = cursor.fetchall()
        cursor.close()
        return ret

    def i(self, table, value):
        column_list = []
        param_list = []
        placeholder_list = []

        for k, v in value.items():
            column_list.append(k)
            param_list.append(v)
            placeholder_list.append('%s')

        sql = 'INSERT INTO ' + table + ' ( ' + ','.join(column_list) + ') VALUES (' + ','.join(placeholder_list) + ')'

        cnx = self._get_cnx()
        cursor = cnx.cursor()
        cursor.execute(sql, param_list)
        cnx.commit()

        ret = cursor.lastrowid
        cursor.close()
        return ret

    def u(self, table, value, where):
        value_column_list = []
        where_column_list = []
        param_list = []

        for k, v in value.items():
            value_column_list.append(k + '=%s')
            param_list.append(v)
        for k, v in where.items():
            where_column_list.append(k + '=%s')
            param_list.append(v)

        sql = 'UPDATE ' + table + ' SET ' + ','.join(value_column_list) + ' WHERE ' + ' AND '.join(where_column_list)

        cnx = self._get_cnx()
        cursor = cnx.cursor()
        cursor.execute(sql, param_list)
        cnx.commit()

        ret = cursor.rowcount
        cursor.close()
        return ret

    def iu(self, table, value, where):
        ret = None

        r_select = self.s(**{'table': table, 'where': where})
        if len(r_select) > 0:
            id = r_select[0]['id']
            self.u(**{'table': table, 'value': value, 'where': {'id': id}})
            ret = id
        else:
            ret = self.i(**{'table': table, 'value': value.copy().update(where)})
        return ret

    def d(self, table, where):
        column_list = []
        param_list = []
        for k, v in where.items():
            column_list.append(k + '=%s')
            param_list.append(v)

        sql = 'DELETE FROM ' + table + ' WHERE ' + ' AND '.join(column_list)
        cnx = self._get_cnx()
        cursor = cnx.cursor()
        cursor.execute(sql, param_list)
        cnx.commit()

        ret = cursor.rowcount
        cursor.close()
        return ret

    def r(self, sql, param):
        ret = False
        cnx = self._get_cnx()

        if re.match('^SELECT', sql, re.I):
            cursor = cnx.cursor()
            cursor.execute(sql, param)
            ret = cursor.fetchall()
            cursor.close()
        else:
            cursor = cnx.cursor()
            cursor.execute(sql, param)
            cnx.commit()
            ret = True
            cursor.close()

        return ret
