import sqlite3
from timeit import default_timer
from pyFile.get_jion_path import song_db_path


class UsingSqlite(object):

    DB_PATH = song_db_path('songs.db')

    def __init__(self, commit=True, log_time=False, log_label='总用时', dict_formate=True):
        """
        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        :param dict_formate:  是否返回字典形式
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label
        self._sql = self.DB_PATH
        self._dict_formate = dict_formate

    def __enter__(self):
        def dict_factory(_cursor, row):
            d = {}
            for index, col in enumerate(_cursor.description):
                d[col[0]] = row[index]
            return d

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        conn = sqlite3.connect(self._sql)
        # 字典形式返回
        if self._dict_formate:
            conn.row_factory = dict_factory
        cursor = conn.cursor()

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    def fetch_one(self, sql, params=()):
        """返回一个结果"""
        # 无参数
        if params is None:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        # 单一参数
        if not type(params) is tuple:
            params = (params,)  # 转换为元组
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        """返回多个结果"""
        # 无参数
        if params is None:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        # 单一参数
        if not type(params) is tuple:
            params = (params,)  # 转换为元组
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    @property  # 将游标转换为只读属性
    def cursor(self):
        return self._cursor
