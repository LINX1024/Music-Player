import json
import os
import re
from collections import Counter
import random
from time import strftime, gmtime
import requests
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from pyFile.Ui_Window import MainWindow
from pyFile.sql_song import Thread, select_songs, remove_sql_db
import sys
from PyQt6.QtCore import Qt, QStringListModel, QUrl, QModelIndex, QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap, QTextCursor, QTextFormat, QBrush
from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow, QMessageBox
from pyFile.get_jion_path import image_path, musics_path


class PlayerWindow(QMainWindow):
    def __init__(self):
        # 继承父类
        super().__init__()
        self.ui = MainWindow()  # 信号
        # 事件过滤器
        self.installEventFilter(self)

        # 初始化
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.song_playlist = []  # 歌曲播放列表
        self.lrc_line_number = 0  # 歌词行计数
        self.is_started = False  # 播放按钮状态
        self.lrc_time_index = 0  # 歌词时间戳标记
        self.song_index = 0  # 歌曲标记
        # self.lrc_time_list = []  # 歌词时间戳列表
        self.play_mode = 0  # 播放模式
        self.volume_mode = False  # 点击的音量
        self.search_text = ""  # 搜索文本
        self.model = None  # 添加的列表数据
        self.lyric_state = False  # 歌词开关
        self.volume_state = True  # 音量开关
        self.lyric_times = []  # 歌词时间
        self.lyric_content = []  # 歌词内容
        self.image_path = image_path
        self.music_path = musics_path
        self.audio_output.setVolume(80)  # 默认音量
        self.player.mediaStatusChanged.connect(self.media_status_changed)

        # 进度条计时器
        self.timer = QTimer(self)
        # self.timer.setSingleShot(True)
        self.timer.setInterval(100)  # 定时器间隔，以毫秒为单位
        self.timer.timeout.connect(self.update_progress_bar)  # 连接到更新进度条的槽函数

        # 歌词计时器
        self.timer_lyric = QTimer(self)
        self.timer_lyric.setInterval(100)
        self.timer_lyric.timeout.connect(self.lyric_do)

        # 按键绑定
        self.ui.icon_button.clicked.connect(self.remove_song_sql)
        self.ui.search_button.clicked.connect(self.get_search_text)
        self.ui.search_button.clicked.connect(self.search_sql)
        self.ui.playlist_down_button.clicked.connect(self.play_list_add)
        self.ui.song_list_button.clicked.connect(self.play_list_add)
        self.ui.playlist_listview.clicked.connect(self.get_play_list_text)
        self.ui.download_button.clicked.connect(self.download_status)
        self.ui.play_button.clicked.connect(self.song_start_switch)
        # self.ui.play_button.clicked.connect(self.start_play)
        self.ui.previous_button.clicked.connect(self.playPrevious)
        self.ui.next_button.clicked.connect(self.playNext)
        self.ui.sort_button.clicked.connect(self.change_play_mode)
        self.ui.lyric_button.clicked.connect(self.lyric_switch)
        self.ui.volume_button.clicked.connect(self.get_volume_state)

        # 创建线程
        # self.ui.signal.connect(self.song_start_switch)
        # self.thread_load_songs.signal_item.connect(self.thread_search_num)
        # self.thread_load_songs.signal_stop.connect(self.thread_search_stop)

    # 强制删除数据库
    def remove_song_sql(self):
        remove_sql_db()

    # 获取搜索框数据
    def get_search_text(self):
        self.search_text = self.ui.search_input.text()
        # self.ui.label_lyr.setText("正在加载中。。。。")

    # 先在数据库中搜索，没有在从网址搜索
    def search_sql(self):
        if self.search_text != "":
            song_data = select_songs(self.search_text)  # 全部数据
            if len(song_data) != 0:
                for i in range(len(song_data)):
                    if self.search_text in song_data[i]["name"] or self.search_text in song_data[i]["singer"] or song_data[i]["name"] == "未知" or song_data[i]["singer"] == "未知":
                        # print(song_data[i]["name"], song_data[i]["singer"])
                        if "歌曲序号: " + str(song_data[i]["id"]) not in self.ui.lyrics_textedit.toPlainText():
                            self.ui.lyrics_textedit.append("歌曲序号: " + str(song_data[i]["id"]))
                            self.ui.lyrics_textedit.append("歌曲名称: " + song_data[i]["name"])
                            self.ui.lyrics_textedit.append("歌手名称: " + song_data[i]["singer"])
                            self.ui.lyrics_textedit.append("歌曲专辑: " + song_data[i]["albumName"])
                            self.ui.lyrics_textedit.append("发行日期: " + song_data[i]["time"] + "\n\n")
                        self.song_playlist.append(
                            str(song_data[i]["id"]) + "." + song_data[i]["name"] + "-" + song_data[i]["singer"])
                    else:
                        QMessageBox.critical(self, f"错误", "音乐未找到,请到酷我音乐搜索试试！！！")
                        break
                return song_data
            else:
                # print(222)
                Thread(self.search_text)
                self.ui.lyrics_textedit.clear()
                self.song_playlist.clear()
                self.play_list_add()
                self.search_sql()
                self.play_list_add()
        else:
            QMessageBox.warning(self, "警告", "搜索框为空，请重新搜索！！")

    # 右侧播放列表添加
    def play_list_add(self):
        self.song_playlist = self.song_playlist.copy()
        counter = Counter(self.song_playlist)  # 去重
        self.song_playlist = [item for item, count in counter.items() if count >= 1]
        self.model = QStringListModel(self.song_playlist)
        self.ui.playlist_listview.setModel(self.model)

    # 点击右侧歌曲后，获得的歌曲名称
    def get_play_list_text(self, index: QModelIndex):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()
            # self.song_pause()
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.stop()
        else:
            pass
        item = self.model.data(index)
        print(index.row())
        song_data = self.search_sql()
        # print(song_data)
        if item and len(song_data) != 0:
            for i in range(len(song_data)):
                if item == str(song_data[i]["id"]) + "." + song_data[i]["name"] + "-" + song_data[i]["singer"]:
                    # print(song_data[i])
                    if song_data[i]["pic"]:
                        response = requests.get(song_data[i]["pic"])
                        image_data = response.content
                        pixmap = QPixmap()
                        pixmap.loadFromData(image_data)
                        self.ui.pic_label.setPixmap(pixmap.scaled(100, 100))
                        self.ui.pic_label.setAlignment(Qt.AlignmentFlag.AlignTop)
                    self.ui.info_label.setText(
                        f"歌曲: \n{song_data[i]['name']}\n\n歌手: \n{song_data[i]['singer']}\n\n专辑: \n{song_data[i]['albumName']}\n\n发行日期: \n{song_data[i]['time']}")
                    # print(song_data[i]["lrcgc"])
                    if '"' in song_data[i]["lrcgc"]:
                        song_data[i]["lrcgc"] = re.sub(r'"(.*?)"', lambda x: '"' + x.group(1).replace("'", "’") + '"',
                                                       song_data[i]["lrcgc"])
                    self.get_lyric_time_content(song_data[i]["lrcgc"].replace("'", '"'))
                    if self.lyric_state is True:
                        self.song_lrc_init()
                    self.play_init(song_data[i]['song_url'])
                    self.song_index = (song_data[i]["id"]) - 1
                    print(item)

    # 获取歌词时间和内容
    def get_lyric_time_content(self, lyrics):
        self.lyric_times.clear()
        self.lyric_content.clear()
        lyrics_json = json.loads(lyrics)  # 转换为 JSON 格式字符串，设置 ensure_ascii=False 可以保留中文字符
        # print(lyrics_json)
        for time, content in lyrics_json.items():
            if 'ti' in time or 'ar' in time or 'al' in time or 'by' in time or 'offset' in time:
                continue
            time_str = time.replace("[", "").replace("]", "")
            # 分割时间字符串，得到分钟和秒的部分
            minutes, seconds = time_str.split(":")

            # 将分钟和秒转换为浮点数
            minutes = float(minutes)
            seconds = float(seconds)

            # 计算总秒数
            total_seconds = minutes * 60 + seconds
            self.lyric_times.append(total_seconds)
            self.lyric_content.append(content)
        # print(self.lyric_times)
        # print(self.lyric_content)

    # 点击下载单曲
    def download_status(self):
        song_data = self.search_sql()
        if song_data is not None:
            song_name = re.findall("歌曲: \n(.*?)\n", self.ui.info_label.text())[0]
            song_singer = re.findall("歌手: \n(.*?)\n", self.ui.info_label.text())[0]
            for i in range(len(song_data)):
                if song_name == song_data[i]["name"] and song_singer == song_data[i]['singer']:
                    # print(song_data[i]['song_url'])
                    self.save_song(song_data[i]['song_url'], song_data[i]['name'],song_data[i]['singer'])

    # 保存单曲
    def save_song(self, song_url, song_name, song_singer):
        if os.path.exists(self.music_path("musics")) is False:
            os.mkdir(self.music_path("musics"))
        response = requests.get(song_url)
        if response.status_code == 200:

            with open(self.music_path(f"musics/{song_name}-{song_singer}.mp3"), "wb") as file:
                file.write(response.content)
            QMessageBox.information(self, "成功", self.music_path(f"{song_name}-{song_singer}") + "下载完成！")
        else:
            QMessageBox.information(self, "错误", "音乐链接地址失效,请重新搜索下载！！！")

    def play_init(self, song_now_path):
        """播放初始化"""
        try:
            self.player.setSource(QUrl(song_now_path))
            self.song_play()
            # if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:

            print(song_now_path)
        except Exception as e:
            QMessageBox.information(self, f"错误:{e}", "音乐链接地址失效！！！")

    def song_play(self):
        """音乐播放"""
        self.player.play()
        self.timer.start(1000)  # 启动定时器
        self.timer_lyric.start()
        self.is_started = True
        print('播放')
        self.ui.play_button.setToolTip('暂停')
        self.ui.play_button.setFixedSize(30, 30)
        self.icon_play = QIcon(self.image_path("播放中.png"))
        # 获取图标大小
        self.icon_play_size = self.ui.play_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.ui.play_button.setIcon(self.icon_play)
        self.ui.play_button.setIconSize(self.icon_play_size)

    def song_pause(self):
        """音乐暂停"""
        self.player.pause()
        self.is_started = False
        print('暂停')
        self.ui.play_button.setToolTip('播放')
        self.ui.play_button.setFixedSize(30, 30)
        self.icon_play = QIcon(self.image_path("暂停.png"))
        # 获取图标大小
        self.icon_play_size = self.ui.play_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.ui.play_button.setIcon(self.icon_play)
        self.ui.play_button.setIconSize(self.icon_play_size)

    # 播放/按钮键切换
    def song_start_switch(self):
        if self.is_started is True:
            self.song_pause()
        else:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
                self.start_play()
            # elif self.player.playbackState() ==  QMediaPlayer.PlaybackState.PausedState:
            else:
                self.song_play()

    # 最初点击播放按钮设置
    def start_play(self):
        song_data = self.search_sql()
        if song_data is not None:
            if len(song_data) > 0:
                data = song_data[self.song_index]
                if data["pic"]:
                    response = requests.get(data["pic"])
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    self.ui.pic_label.setPixmap(pixmap.scaled(100, 100))
                    self.ui.pic_label.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.ui.info_label.setText(
                    f"歌曲: \n{data['name']}\n\n歌手: \n{data['singer']}\n\n专辑: \n{data['albumName']}\n\n发行日期: \n{data['time']}")
                print(data["song_url"])
                self.play_init(data["song_url"])
                if '"' in data["lrcgc"]:
                    data["lrcgc"] = re.sub(r'"(.*?)"', lambda x: '"' + x.group(1).replace("'", "’") + '"',
                                           data["lrcgc"])
                self.get_lyric_time_content(data["lrcgc"].replace("'", '"'))
                if self.lyric_state is True:
                    self.song_lrc_init()
        else:
            QMessageBox.information(self, f"错误", "播放列表为空，请重新搜索加载")

    # 播放结束后，自动下一首
    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            if self.song_index < (len(self.search_sql()) - 1):
                print("媒体文件播放到达结尾")
                self.song_index += 1
                if self.play_mode == 0:
                    pass
                elif self.play_mode == 1:
                    self.player.stop()
                    self.player.setPosition(0)
                    self.song_index -= 1
                else:
                    if self.search_sql():
                        self.song_index = random.randint(0, len(self.search_sql()) - 1)
                self.start_play()
                print(self.song_index)
            else:
                self.song_index = 0
                self.start_play()

    # 上一首设置
    def playPrevious(self):
        if self.song_index != 0:
            self.player.stop()
            self.song_index -= 1
            self.start_play()
        else:
            self.song_index = len(self.search_sql()) - 1
            self.player.stop()
            self.start_play()

    # 下一首设置
    def playNext(self):
        if self.song_index < (len(self.search_sql()) - 1):
            self.song_index += 1
            self.player.stop()
            self.start_play()
        else:
            print(self.song_index, 1111)
            self.player.stop()
            self.song_index = 0
            self.start_play()

    def change_play_mode(self):
        """
        切换播放模式
        0 => 顺序播放
        1 => 单曲循环
        2 => 随机播放
        """
        self.play_mode += 1
        if self.play_mode > 2:
            self.play_mode = 0
        self.sort_play()

    # 播放顺序设置
    def sort_play(self):
        if self.play_mode == 0:  # 默认顺序播放
            self.ui.sort_button.setToolTip("列表循环")
            self.ui.sort_button.setFixedSize(30, 30)
            self.icon_sort = QIcon(self.image_path("列表循环.png"))
            # 获取图标大小
            self.icon_sort_size = self.ui.sort_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.sort_button.setIcon(self.icon_sort)
            self.ui.sort_button.setIconSize(self.icon_sort_size)
            # 设置扁平样式
            self.ui.sort_button.setFlat(True)

        elif self.play_mode == 1:  # 单曲循环
            self.ui.sort_button.setToolTip("单曲循环")
            self.ui.sort_button.setFixedSize(30, 30)
            self.icon_sort = QIcon(self.image_path("单曲循环.png"))
            # 获取图标大小
            self.icon_sort_size = self.ui.sort_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.sort_button.setIcon(self.icon_sort)
            self.ui.sort_button.setIconSize(self.icon_sort_size)
            # 设置扁平样式
            self.ui.sort_button.setFlat(True)
            # self.song_index -= 1
        elif self.play_mode == 2:  # 随机播放
            self.ui.sort_button.setToolTip("随机播放")
            self.ui.sort_button.setFixedSize(30, 30)
            self.icon_sort = QIcon(self.image_path("随机播放.png"))
            # 获取图标大小
            self.icon_sort_size = self.ui.sort_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.sort_button.setIcon(self.icon_sort)
            self.ui.sort_button.setIconSize(self.icon_sort_size)
            # 设置扁平样式
            self.ui.sort_button.setFlat(True)
            # if self.search_sql():
            #     self.song_index = random.randint(0, len(self.search_sql()) - 1)

    # 进度条设置
    def update_progress_bar(self):
        duration = self.player.duration() / 1000  # 将歌曲总时长转换为秒
        self.ui.song_time_label.setText(strftime("%M:%S", gmtime(duration)))  # 显示歌曲总时长00:00 格式
        position = self.player.position() / 1000  # 将当前播放位置转换为秒
        self.ui.start_time_label.setText(strftime("%M:%S", gmtime(position)))  # 显示歌曲当前时长00:00 格式
        if duration != 0:
            progress = position / duration * 100  # 计算进度百分比
            self.ui.progress_Bar.setValue(int(progress))  # 设置进度条的值
        else:
            QMessageBox.information(self, f"错误", "播放链接失效，请点击图标按钮删除数据，重新搜索加载")
            self.timer.stop()
            self.timer_lyric.stop()

    # 歌词开关设置
    def lyric_switch(self):
        if self.lyric_state is True:
            self.ui.lyrics_textedit.clear()
            self.search_sql()
            self.ui.lyric_button.setToolTip('歌词关闭')
            self.ui.lyric_button.setFixedSize(30, 30)
            self.icon_lyric = QIcon(self.image_path("candle_off.png"))
            # 获取图标大小
            self.icon_lyric_size = self.ui.lyric_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.lyric_button.setIcon(self.icon_lyric)
            self.ui.lyric_button.setIconSize(self.icon_lyric_size)
            self.lyric_state = False
        else:
            self.ui.lyrics_textedit.clear()
            self.song_lrc_init()
            self.ui.lyric_button.setToolTip('歌词开启')
            self.ui.lyric_button.setFixedSize(30, 30)
            self.icon_lyric = QIcon(self.image_path("candle_on.png"))
            # 获取图标大小
            self.icon_lyric_size = self.ui.lyric_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.lyric_button.setIcon(self.icon_lyric)
            self.ui.lyric_button.setIconSize(self.icon_lyric_size)
            self.lyric_state = True

    def song_lrc_init(self):
        """歌词初始化"""
        self.ui.lyrics_textedit.clear()
        for lyric in self.lyric_content:
            self.ui.lyrics_textedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.lyrics_textedit.append(lyric + "\n")

    # 音量按钮设置
    def get_volume_state(self):
        if self.volume_state:
            self.audio_output.setVolume(0)
            self.volume_state = False
            self.ui.volume_button.setToolTip('静音状态')
            self.ui.volume_button.setFixedSize(30, 30)
            self.icon_volume = QIcon(self.image_path("volume_off.png"))
            # 获取图标大小
            self.icon_volume_size = self.ui.volume_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.volume_button.setIcon(self.icon_volume)
            self.ui.volume_button.setIconSize(self.icon_volume_size)
        else:
            self.audio_output.setVolume(80)
            self.volume_state = True
            self.ui.volume_button.setToolTip('响铃状态')
            self.ui.volume_button.setFixedSize(30, 30)
            self.icon_volume = QIcon(self.image_path("volume_on.png"))
            # 获取图标大小
            self.icon_volume_size = self.ui.volume_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.ui.volume_button.setIcon(self.icon_volume)
            self.ui.volume_button.setIconSize(self.icon_volume_size)

    def lyric_do(self):
        self.lrc_time_index = self.find_current_lyric((self.player.position() / 1000), self.lyric_times)
        # print(self.lrc_time_index, self.lyric_content)
        if self.lrc_time_index < 0:
            self.ui.label_lyr.setText("暂无歌词")
            self.ui.lyrics_textedit.setText("暂无歌词")
        else:
            if self.lrc_time_index >= len(self.lyric_times):
                self.ui.label_lyr.setText("歌曲即将结束。。。。。")
            elif (self.player.position() / 1000) >= self.lyric_times[self.lrc_time_index]:
                self.ui.label_lyr.setText(self.lyric_content[self.lrc_time_index])
                self.ui.label_lyr.setStyleSheet(
                    f"QLabel {{ color: {'green' if self.lrc_time_index <= 1 else 'yellow'}; font-weight: bold}}")
                # print(self.lyric_content[self.lrc_time_index],1111, self.get_line_text(self.lrc_time_index * 2),222)
                if self.lyric_content[self.lrc_time_index] == self.get_line_text(self.lrc_time_index * 2):
                    self.replace_line(self.lrc_time_index * 2, self.lyric_content[self.lrc_time_index])
                self.lrc_time_index += 1
            else:
                return

    # 获取当前歌词时间的索引值
    def find_current_lyric(self, position, lyric_times):
        for i in range(len(lyric_times)):
            if position < lyric_times[i]:
                return i - 1 if i > 0 else 0
        return len(lyric_times) - 1

    def get_line_text(self, line_number):
        cursor = self.ui.lyrics_textedit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        for _ in range(line_number):
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        selected_text = cursor.selectedText()
        # print(selected_text)
        return selected_text

    def replace_line(self, line_number, new_text):
        cursor = self.ui.lyrics_textedit.textCursor()
        cursor.setPosition(cursor.anchor())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number)

        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)

        # # 歌词高亮颜色
        highlight_color = QTextEdit.ExtraSelection()

        # 设置高亮颜色
        highlight_color.format.setForeground(QBrush(QColor("purple")))
        highlight_color.format.setFontPointSize(18)
        highlight_color.format.setProperty(QTextFormat.Property.FullWidthSelection, True)

        # 设置高亮行
        highlight_color.cursor = cursor
        self.ui.lyrics_textedit.setExtraSelections([highlight_color])
        self.ui.lyrics_textedit.setTextCursor(cursor)

    # def keyPressEvent(self, event: QKeyEvent):
    #     """按键响应事件"""
    #     print("按下：" + str(event.key()))
    #     if self.ui.keyReleaseEvent(event) == Qt.Key.Key_Enter:
    #         self.search_sql()
    #     elif self.ui.keyReleaseEvent(event) == Qt.Key.Key_Space:
    #         self.song_start_switch()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 声明应用程序
    player_window = PlayerWindow()  # 声明窗口
    sys.exit(app.exec())
