import os


def image_path(img_path):
    """
    拼接路径
    :param img_path: 路径1
    :return: icon_path
    """
    # 获取当前文件的绝对路径
    current_dir = (os.path.dirname(os.path.abspath(__file__))).replace('/pyFile', '')
    images_dir = os.path.join(current_dir, 'images')
    icon_path = os.path.join(images_dir, img_path)
    return icon_path


def song_db_path(db_path):
    """
    拼接路径
    :param db_path: 路径1
    :return: icon_path
    """
    # 获取当前文件的绝对路径
    current_dir = (os.path.dirname(os.path.abspath(__file__))).replace('/pyFile', '')
    sql_config_dir = os.path.join(current_dir, 'sqlConfig')
    db_path = os.path.join(sql_config_dir, db_path)
    return db_path


def musics_path(music_path):
    """
    拼接路径
    :param music_path: 路径1
    :return: music_path
    """
    # 获取当前文件的绝对路径
    current_dir = os.path.expanduser("~")
    download_path = os.path.join(current_dir, 'Downloads')
    music_path = os.path.join(download_path, music_path)
    return music_path

