import re
import asyncio
import aiohttp
import json


class OnlineInfo:
    def __init__(self):
        self.headers = {
            'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        self.session = aiohttp.ClientSession(headers=self.headers)  # 将用于异步HTTP请求的session

    # async def init_session(self):
    #     self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        await self.session.close()

    async def get_music_info_async(self, item_name):
        # 异步版本的get_music_info
        song_data = []
        url = 'http://www.kuwo.cn/search/searchMusicBykeyWord?vipver=1&client=kt&ft=music&cluster=0&strategy=2012&encoding=utf8&rformat=json&mobi=1&issubtitle=1&show_copyright_off=1&pn=0&rn=10&all={}'.format(
            item_name)
        async with self.session.get(url) as response:
            res_js = json.loads(await response.text())
            song_lists = res_js['abslist']
            for song in song_lists:
                song_rid = song['MUSICRID'].replace('MUSIC_', '')
                song_name = song['SONGNAME'] if song['SONGNAME'] != '' else '未知'
                song_artist = song['ARTIST'] if song['ARTIST'] != '' else '未知'
                song_album = song['ALBUM'] if song['ALBUM'] != '' else '未知'
                song_duration = song['web_timingonline'].split(' ')[0] if song['web_timingonline'] != '' else '未知'
                song_pic = "https://img2.kuwo.cn/star/albumcover/" + song['web_albumpic_short'] if song[
                                                                                                       'web_albumpic_short'] != '' else None
                song_data.append({"mid": song_rid, "name": song_name, "singer": song_artist, "albumName": song_album,
                                  "pic": song_pic, "time": song_duration})
        return song_data

    async def get_song_info_async(self, song_rid):
        # 异步获取歌曲详细信息的辅助函数
        url = f'https://api.cenguigui.cn/api/kuwo/?rid={song_rid}&type=json&level=exhigh&lrc=true'
        async with self.session.get(url) as response:
            song_info = await response.json()
            song_url = song_info['data']['url'] if song_info['data']['url'] != None else None
            song_lrc = song_info['data']['lrc'] if song_info['data']['lrc'] != None else '未知'
            return {"song_url": song_url, "lrcgc": song_lrc}

    async def fetch_all_song_infos(self, song_rids):
        # 并发获取多个歌曲信息的协程
        tasks = [self.get_song_info_async(rid) for rid in song_rids]
        song_infos = await asyncio.gather(*tasks)
        return song_infos


def get_lyric(lrc_list_raw):
    def timestamp_to_dict(lrc_list):
        # 时间戳正则
        func = re.compile("\\[.*?]")
        # 根据时间戳，转换成字典
        _lrc_dict = {}
        for _i in lrc_list:
            if func.search(_i) is None:
                continue
            lrc_time = func.search(_i).group()
            lrc_text = func.sub('', _i)
            lrc_text = ' '.join(lrc_text.split())
            _lrc_dict[lrc_time] = lrc_text
        return _lrc_dict

    return timestamp_to_dict(lrc_list_raw.splitlines())


async def online_info(input_text):
    online_info = OnlineInfo()
    song_data_list = await online_info.get_music_info_async(input_text)
    mids = [song_data['mid'] for song_data in song_data_list]
    song_info_list = await online_info.fetch_all_song_infos(mids)
    for song_data, song_info in zip(song_data_list, song_info_list):
        song_data["song_url"] = song_info["song_url"]
        song_data["lrcgc"] = song_info["lrcgc"]
    await online_info.close_session()
    return song_data_list


if __name__ == '__main__':
    # 运行主协程
    asyncio.run(online_info('周杰伦'))
