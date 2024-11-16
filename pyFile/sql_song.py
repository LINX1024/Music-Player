import os
import asyncio
from PyQt6.QtCore import QThread
from .sqlite_lib import UsingSqlite
from .kuwo_music import online_info, get_lyric


class Thread(QThread):
    """子线程类"""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.online_info = online_info
        self.run()

    def run(self):
        """重写执行方法"""
        self.creat_song_table()

    def creat_song_table(self):
        """建立数据库，建立表单，存储数据"""
        with UsingSqlite() as us:
            us.cursor.execute("drop table if exists music_info")
            us.cursor.execute("""
                CREATE TABLE IF NOT EXISTS music_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid TEXT,
                name TEXT,
                singer TEXT,
                albumName TEXT,
                pic TEXT,
                time TEXT,
                song_url TEXT,
                lrcgc TEXT
                )
            """)
            insert_query = """
                INSERT INTO music_info (mid, name, singer, albumName, pic, time, song_url, lrcgc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            file_num = 0
            music_infos = asyncio.run(self.online_info(self.text))

            for info in music_infos:
                lrcgc = get_lyric(info['lrcgc'])

                us.cursor.execute(insert_query,
                                  (info['mid'], info['name'], info['singer'], info['albumName'], info['pic'],
                                   info['time'], info['song_url'], str(lrcgc)))
                file_num += 1


def select_songs(text):
    """搜索数据库数据"""
    if not os.path.exists(UsingSqlite.DB_PATH):
        Thread(text)
    # print(text)
    with UsingSqlite() as us:
        text = '%{}%'.format(text)
        sql = """
            select * from music_info
            where mid like ? or name like ? or singer like ? or albumName like ? or pic like ? or time like ? or song_url like ? or lrcgc like ?
        """
        params = (text, text, text, text, text, text, text, text)
        result = us.fetch_all(sql, params)
        return result


def remove_sql_db():
    if os.path.exists(UsingSqlite.DB_PATH):
        # 删除文件
        os.remove(UsingSqlite.DB_PATH)
        print(f"{UsingSqlite.DB_PATH} 已删除")
    else:
        print(f"{UsingSqlite.DB_PATH} 不存在，无法删除")


if __name__ == "__main__":
    # t = Thread("周杰伦")
    print(select_songs("白鸽"))
