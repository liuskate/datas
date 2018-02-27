#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 11:26:39 2017

@author: ghk29
"""

import requests
import json
import os
import warnings
import datetime
import time
import sys
import traceback
import commands
from util import log
from datetime import datetime

warnings.filterwarnings("ignore")
LOG = log.init_log("./log/download", __name__)

"""

QQ音乐自己找的接口

歌单的接口       （参数：disstid 歌单）
    https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&disstid=2973463430

歌手的接口    （参数：singermid)
    https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?format=json&singermid=000foEm54CJUqL&order=listen&begin=0&num=1000

歌手的热门歌曲：
    https://c.y.qq.com/rsc/fcgi-bin/fcg_order_singer_getnum.fcg?format=json&singermid=001oEyQf4Ub6s7"

搜索接口
https://c.y.qq.com/soso/fcgi-bin/client_search_cp?t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=60&w=%E5%91%A8%E6%9D%B0%E4%BC%A6&format=json

"""



class QQMusicDownloader(object):
    
    def __init__(self, store_path = "./qq_music"):
        self.store_path = store_path
        self.search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w=%s'
        self.get_vkey_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?&jsonpCallback=MusicJsonCallback&cid=205361747&songmid=%s&filename=C400%s.m4a&guid=6612300644'
        self.download_url = 'http://dl.stream.qqmusic.qq.com/C400%s.m4a?vkey=%s&guid=6612300644&uin=0&fromtag=66'
 
        
    def search(self, word):
        search_url = self.search_url % (word)
        res = requests.get(search_url, verify=False)
        jml = json.loads(res.text.strip('callback()[]'))['data']['song']['list']
        return [{
                    "songmid": i["songmid"],
                    "songname": i["songname"],
                    "singers": i['singer'][0]['name'],
                } for i in jml]
    
    def get_download_url(self, songmid):
        res = requests.get(self.get_vkey_url %(songmid, songmid), verify=False)
        try:
            vkey = json.loads(res.text)['data']['items'][0]['vkey']
            return self.download_url % (songmid, vkey)
        except:
            LOG.error(songmid)
            return None
        
    def _download_music(self, music_url, music_file_name):
        print('***** '+music_file_name+' *****'+' Downloading...')
        try:
            r = requests.get(music_url, verify=False)
        except Exception as e:
            print('Download wrong occur in download_music')
            traceback.print_exc()
            return
        try:
            with open(os.path.join(self.store_path, music_file_name), "wb") as code:
                 code.write(r.content)
        except Exception as e:
            print('save wrong~')
            print(e)
            if music_file_name in os.listdir(self.store_path):
                os.remove(os.path.join(self.store_path, music_file_name))

    def download_music(self, url, path, limit_rate="2M", timeout=20):
        try:
            command = "curl \"%s\" --limit-rate \"%s\" --max-time \"%s\" -o \"%s\"" % (url, limit_rate, timeout, path)
            code, output = commands.getstatusoutput(command)
            if code != 0:
                LOG.error(url)
            else:
                LOG.info(url)
        except Exception as e:
            print('Download wrong occur in download_music')
            traceback.print_exc()
            return
    
    def _get_store_path(self):
        today = datetime.today().strftime('%Y%m%d')
        store_path = os.path.join(self.store_path, today)
        if not os.path.exists(store_path):
            os.makedirs(store_path, 0755)
        return store_path

    def download_by_songmid(self, songmid):
        try:
            songmid=songmid.strip('\n').split('\t')[0]
            filename = '%s.m4a' %(songmid)
            path = os.path.join(self._get_store_path(), filename)
            print path
            url = self.get_download_url(songmid)
            if url:
                self.download_music(url, path)
        except Exception as e:
            print('Download wrong occur in download_by_songmid')
            traceback.print_exc()
            
    

if __name__ == "__main__":
    store_dir = sys.argv[1]
    qq_music = QQMusicDownloader(store_dir)
    qq_music.download_by_songmid("003S1hgM2asCye")
