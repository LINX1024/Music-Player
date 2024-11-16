import sys
from PyQt6.QtCore import QSize, Qt, QStringListModel, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListView, QTextEdit, QLineEdit, \
    QPushButton, QProgressBar, QScrollArea
from pyFile.get_jion_path import image_path


class MainWindow(QWidget):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Player")
        self.resize(850, 650)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole(QPalette.ColorRole.Window), QColor(34, 40, 49))  # 设置窗口背景颜色
        palette.setColor(QPalette.ColorRole(QPalette.ColorRole.WindowText), QColor(255, 255, 255))  # 设置窗口文字颜色
        self.setPalette(palette)
        self.listview_state = False
        self.song_name = "暂无"
        self.singer = "暂无"
        self.album_name = "暂无"
        self.song_time = "暂无"
        self.image_path = image_path

        self.setupUI()
        self.show()

    def setupUI(self):
        self.window_layout = QVBoxLayout(self)
        # 创建主要布局
        self.layout_top = QHBoxLayout()
        self.layout_middle = QHBoxLayout()
        self.layout_lyr_bott = QHBoxLayout()
        self.layout_bottom = QHBoxLayout()

        self.window_layout.addLayout(self.layout_top)
        self.window_layout.addLayout(self.layout_middle)
        self.window_layout.addLayout(self.layout_lyr_bott)
        self.window_layout.addLayout(self.layout_bottom)

        # 创建搜索布局
        self.search_layout = QHBoxLayout()
        self.layout_top.addLayout(self.search_layout)

        # 图标按钮
        self.icon_button = QPushButton()
        self.icon_button.setToolTip('hi, 欢迎来到我的音乐')
        self.icon_button.setFixedSize(50, 50)
        self.icon_music = QIcon(self.image_path("music.png"))
        # 获取图标大小
        self.icon_music_size = self.icon_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.icon_button.setIcon(self.icon_music)
        self.icon_button.setIconSize(self.icon_music_size)
        # 设置扁平样式
        self.icon_button.setFlat(True)
        self.search_layout.addWidget(self.icon_button)

        # 创建搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入歌曲名或歌手名")
        self.search_input.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #3498db;
                        border-radius: 5px;
                        padding: 5px;
                        background-color: #f2f2f2;
                        color: #333333;
                    }
                    QLineEdit:focus {
                        border: 2px solid red;
                        background-color: #ffffff;
                    }
        """)
        self.search_layout.addWidget(self.search_input)

        # 创建搜索按钮
        self.search_button = QPushButton()
        self.search_button.setToolTip('搜索')
        self.search_button.setFixedSize(40, 40)
        self.icon_search = QIcon(self.image_path("search.png"))
        # 获取图标大小
        self.icon_search_size = self.search_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.search_button.setIcon(self.icon_search)
        self.search_button.setIconSize(self.icon_search_size)
        # 设置扁平样式
        self.search_button.setFlat(True)
        self.search_layout.addWidget(self.search_button)

        # 创建左侧垂直布局
        self.left_layout = QVBoxLayout()
        self.layout_middle.addLayout(self.left_layout)

        # 创建播放歌曲信息标签
        self.pic_label = QLabel()
        self.pixmap = QPixmap(self.image_path("Nagisa.png")).scaled(100, 100)
        self.pic_label.setPixmap(self.pixmap)
        self.pic_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_layout.addWidget(self.pic_label)

        # 显示歌曲信息
        self.info_label = QLabel()
        self.info_label.setText(
            f"歌曲: {self.song_name}\n\n歌手: {self.singer}\n\n专辑: {self.album_name}\n\n日期: {self.song_time}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.left_layout.addWidget(self.info_label)

        self.download_layout = QHBoxLayout()
        self.left_layout.addLayout(self.download_layout)

        self.download_label = QLabel()
        self.download_label.setText(f"歌曲下载:")
        self.download_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.download_layout.addWidget(self.download_label)

        # 歌曲下载
        self.download_button = QPushButton()
        self.download_button.setToolTip("下载歌曲")
        self.download_button.setFixedSize(25, 25)
        self.icon_download = QIcon(self.image_path("cloud_download.png"))
        # 获取图标大小
        self.icon_download_size = self.download_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.download_button.setIcon(self.icon_download)
        self.download_button.setIconSize(self.icon_download_size)
        # 设置扁平样式
        self.download_button.setFlat(True)
        self.download_layout.addWidget(self.download_button)

        # 创建中间布局
        self.middle_layout = QVBoxLayout()
        self.layout_middle.addLayout(self.middle_layout)

        # 创建歌词显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.lyrics_textedit = QTextEdit()
        self.lyrics_textedit.setReadOnly(True)
        self.lyrics_textedit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.lyrics_textedit.setStyleSheet("background-color: gray; color: white; font-weight: bold;font-size: 16pt;")
        # self.lyrics_textedit.setStyleSheet("QLabel {qproperty-alignment: 'AlignCenter'; color: white; font-weight: bold;}")
        self.scroll_area.setWidget(self.lyrics_textedit)
        self.middle_layout.addWidget(self.scroll_area)

        # 创建右侧布局
        self.right_layout = QVBoxLayout()
        self.layout_middle.addLayout(self.right_layout)

        # 创建播放列表标签
        self.playlist_down_button = QPushButton()
        self.playlist_down_button.setToolTip("显示歌曲")
        self.playlist_down_button.setFixedSize(20, 20)
        self.icon_playlist_down = QIcon(self.image_path("arrow-down-bold.png"))
        # 获取图标大小
        self.icon_playlist_down_size = self.playlist_down_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.playlist_down_button.setIcon(self.icon_playlist_down)
        self.playlist_down_button.setIconSize(self.icon_playlist_down_size)
        # 设置扁平样式
        self.playlist_down_button.setFlat(True)
        self.right_layout.addWidget(self.playlist_down_button)

        # 创建播放列表视图
        self.playlist_listview = QListView()
        self.playlist_listview.setStyleSheet("background-color: gray; color: white; font-weight: bold;font-size: 16pt;")
        # 创建一个字符串列表模型
        string_list = ["1.暂无", "2.暂无", "3.暂无"]
        self.model = QStringListModel(string_list)

        # 将模型设置为ListView的模型
        self.playlist_listview.setModel(self.model)
        # 设置ListView的固定大小
        self.playlist_listview.setFixedSize(200, 450)
        self.right_layout.addWidget(self.playlist_listview)

        self.label_layout = QVBoxLayout()
        self.layout_lyr_bott.addLayout(self.label_layout)
        self.label_lyr = QLabel("歌词显示")
        self.label_lyr.setStyleSheet(
            "QLabel {qproperty-alignment: 'AlignCenter'; color: white; font-weight: bold;}")
        self.label_layout.addWidget(self.label_lyr)

        # 创建播放控件布局
        self.play_layout = QHBoxLayout()
        self.layout_bottom.addLayout(self.play_layout)

        # 创建播放控件
        self.previous_button = QPushButton()
        self.previous_button.setToolTip("上一首")
        self.previous_button.setFixedSize(30, 30)
        self.icon_previous = QIcon(self.image_path("上一曲.png"))
        # 获取图标大小
        self.icon_previous_size = self.previous_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.previous_button.setIcon(self.icon_previous)
        self.previous_button.setIconSize(self.icon_previous_size)
        # 设置扁平样式
        self.previous_button.setFlat(True)
        self.play_layout.addWidget(self.previous_button)

        self.play_button = QPushButton()
        self.play_button.setToolTip("播放")
        self.play_button.setFixedSize(30, 30)
        self.icon_play = QIcon(self.image_path("暂停.png"))
        # 获取图标大小
        self.icon_play_size = self.play_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.play_button.setIcon(self.icon_play)
        self.play_button.setIconSize(self.icon_play_size)
        # 设置扁平样式
        self.play_button.setFlat(True)
        self.play_layout.addWidget(self.play_button)

        self.next_button = QPushButton()
        self.next_button.setToolTip("下一首")
        self.next_button.setFixedSize(30, 30)
        self.icon_next = QIcon(self.image_path("下一曲.png"))
        # 获取图标大小
        self.icon_next_size = self.next_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.next_button.setIcon(self.icon_next)
        self.next_button.setIconSize(self.icon_next_size)
        # 设置扁平样式
        self.next_button.setFlat(True)
        self.play_layout.addWidget(self.next_button)

        self.sort_button = QPushButton()
        self.sort_button.setToolTip("列表循环")
        self.sort_button.setFixedSize(30, 30)
        self.icon_sort = QIcon(self.image_path("列表循环.png"))
        # 获取图标大小
        self.icon_sort_size = self.sort_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.sort_button.setIcon(self.icon_sort)
        self.sort_button.setIconSize(self.icon_sort_size)
        # 设置扁平样式
        self.sort_button.setFlat(True)
        self.play_layout.addWidget(self.sort_button)

        self.start_time_label = QLabel("00:00")
        self.start_time_label.setStyleSheet(
            "QLabel {qproperty-alignment: 'AlignCenter'; color: white; font-weight: bold;}")
        self.play_layout.addWidget(self.start_time_label)

        self.progress_Bar = QProgressBar()
        self.progress_Bar.setMouseTracking(True)
        self.progress_Bar.setMaximumSize(QSize(350, 10))
        self.progress_Bar.setMinimum(0)
        self.progress_Bar.setMaximum(100)
        self.progress_Bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid black;
                        border-radius: 5px;
                        text-align: right; /* 文字右对齐 */
                        background-color: #FFFFFF;      
                    }}
                    QProgressBar::chunk {{
                        border: none;
                        background-color: qlineargradient(stop:0 #3498db, stop:10 #3498db, stop:10 transparent, stop:1 transparent);
                    }}
                    QProgressBar::chunk::first {{
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                    }}
                    QProgressBar::chunk::last {{
                        border-top-right-radius: 5px;
                        border-bottom-right-radius: 5px;
                    }}
                    QProgressBar::chunk:hover {{
                        background-color: rgba(52, 152, 219, 0.8);
                    }}
                    QProgressBar {{
                        background-repeat: no-repeat;
                        background-position: center right;
                        background-origin: content;
                        background-clip: content;
                    }}
                    QProgressBar::chunk {{
                        width: 5px;
                    }}

                    """
                                        )
        self.play_layout.addWidget(self.progress_Bar)

        self.song_time_label = QLabel("00:00")
        self.song_time_label.setStyleSheet(
            "QLabel {qproperty-alignment: 'AlignCenter'; color: white; font-weight: bold;}")
        self.play_layout.addWidget(self.song_time_label)

        self.lyric_button = QPushButton()
        self.lyric_button.setToolTip("歌词显示")
        self.lyric_button.setFixedSize(30, 30)
        self.icon_lyric = QIcon(self.image_path("candle_off.png"))
        # 获取图标大小
        self.icon_lyric_size = self.lyric_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.lyric_button.setIcon(self.icon_lyric)
        self.lyric_button.setIconSize(self.icon_lyric_size)
        # 设置扁平样式
        self.lyric_button.setFlat(True)
        self.play_layout.addWidget(self.lyric_button)

        self.volume_button = QPushButton()
        self.volume_button.setToolTip("音量开启")
        self.volume_button.setFixedSize(30, 30)
        self.icon_volume = QIcon(self.image_path("volume_on.png"))
        # 获取图标大小
        self.icon_volume_size = self.volume_button.size()
        # 设置按钮的填充模式为 IconOnly
        self.volume_button.setIcon(self.icon_volume)
        self.volume_button.setIconSize(self.icon_volume_size)
        # 设置扁平样式
        self.volume_button.setFlat(True)
        self.play_layout.addWidget(self.volume_button)

        self.song_list_button = QPushButton()
        self.song_list_button.setToolTip("歌曲列表显示")
        self.song_list_button.setFixedSize(30, 30)
        self.icon_song_list = QIcon(self.image_path("play_list_off.png"))
        # 获取图标大小
        self.icon_song_list_size = self.song_list_button.size()
        self.song_list_button.setIcon(self.icon_song_list)
        self.song_list_button.setIconSize(self.icon_song_list_size)
        # 设置扁平样式
        self.song_list_button.setFlat(True)
        self.play_layout.addWidget(self.song_list_button)
        self.playlist_listview.setVisible(False)

        # 设置按钮
        self.song_list_button.clicked.connect(self.hide_playlist)
        self.playlist_down_button.clicked.connect(self.hide_playlist)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:  # 监听空格键
            # print("空格键")
        # elif (event.key() + 1) == Qt.Key.Key_Enter:  # 监听回车键
        #     print("回车键")
            self.signal.emit()
        # return event.key()


    # 隐藏/显示播放列表的方法
    def hide_playlist(self):
        if self.listview_state is False:
            self.playlist_listview.setVisible(True)
            self.listview_state = True
            self.playlist_down_button.setToolTip("隐藏歌曲")
            self.playlist_down_button.setFixedSize(20, 20)
            self.icon_playlist_down = QIcon(self.image_path("arrow-up-bold"))
            # 获取图标大小
            self.icon_playlist_down_size = self.playlist_down_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.playlist_down_button.setIcon(self.icon_playlist_down)
            self.playlist_down_button.setIconSize(self.icon_playlist_down_size)
            # 设置扁平样式
            self.playlist_down_button.setFlat(True)
        else:
            self.playlist_listview.setVisible(False)
            self.listview_state = False
            self.playlist_down_button.setToolTip("显示歌曲")
            self.playlist_down_button.setFixedSize(20, 20)
            self.icon_playlist_down = QIcon(self.image_path("arrow-down-bold.png"))
            # 获取图标大小
            self.icon_playlist_down_size = self.playlist_down_button.size()
            # 设置按钮的填充模式为 IconOnly
            self.playlist_down_button.setIcon(self.icon_playlist_down)
            self.playlist_down_button.setIconSize(self.icon_playlist_down_size)
            # 设置扁平样式
            self.playlist_down_button.setFlat(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    sys.exit(app.exec())
