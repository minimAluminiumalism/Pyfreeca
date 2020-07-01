import requests
import re
import m3u8
import json
import os
from bs4 import BeautifulSoup


class AfreecaExtractor(object):
    def __init__(self):
        URL = input("stream url: ")
        self.base_url = str(URL)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            "Origin": "http://vod.afreecatv.com",

        }
        self.username = json.load(open("../config.json", "r")).get("username")
        self.password = json.load(open("../config.json", "r")).get("password")
        self.video_info_url = "http://afbbs.afreecatv.com:8080/api/video/get_video_info.php?type=station&isAfreeca=true&autoPlay=true&showChat=true&expansion=true&{}&{}&{}&{}&{}&szPart=REVIEW&szVodType=STATION&szSysType=html5"
        self.login_url = "https://login.afreecatv.com/app/LoginAction.php"
        self.session = requests.Session()

    def login_in(self):
        form_data = {
            "szWork": "login",
            "szType": "json",
            "szUid": self.username,
            "szPassword": self.password,
            "isSaveId": "true",
            "szScriptVar": "oLoginRet",
            "szAction": ""
        }
        login_in = self.session.post(self.login_url, data=form_data)

    def get_video_info_url(self):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            video_info_url = soup.find("head").find("meta", {"name": "twitter:player"})["value"]

            patterns = re.compile(
                "szBjId=(.*?)&.*?nStationNo=(.*?)&.*?nBbsNo=(.*?)&.*?nTitleNo=(.*?)&.*?szCategory=(.*?)&", re.S)
            elem_dict = {}
            elem_list = re.findall(patterns, video_info_url)
            elem_dict["szBjId"] = elem_list[0][0]
            elem_dict["nStationNo"] = elem_list[0][1]
            elem_dict["nBbsNo"] = elem_list[0][2]
            elem_dict["nTitleNo"] = elem_list[0][3]
            elem_dict["szCategory"] = elem_list[0][4]

            bj_name = elem_dict["szBjId"]
            url_elem_list = []
            for key, value in elem_dict.items():
                url_elem_list.append("{}={}".format(key, value))
            video_info_url = self.video_info_url.format(url_elem_list[0], url_elem_list[1], url_elem_list[2],
                                                        url_elem_list[3], url_elem_list[4])
            return video_info_url, bj_name

        else:
            print(response.status_code, "failed to get video info.")
            return None

    def get_all_playlist(self, video_info_url):
        response = self.session.get(video_info_url, headers=self.headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            items = soup.find("video", thumbnail="true").find_all("file")
            # items = soup.find("video", {"duration": True})

            m3u8_playlist_list = []
            patterns = re.compile("http(.*?)m3u8", re.S)
            for item in items:
                url = re.findall(patterns, str(item))
                m3u8_playlist_list.append("http{}m3u8".format(url[0]))
            return m3u8_playlist_list
        else:
            print(response.status_code, "failed to get all playlist.")

        def get_video_name(self):
            response = self.session.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                name = soup.find("title").text
                print("Video Name: ", name)
                return name
            else:
                print(response.status_code, " failed to get video name")

    def get_video_name(self, bj_name):
        response = self.session.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            name = soup.find('ul', id="vodDetailView").find('li').find('span').text.split(' ')[0].replace('-', '')
            video_name = bj_name + '_' + name
            print("Video Name: ", video_name)
            return video_name
        else:
            print(response.status_code, " failed to get video name")

    def resolution_confirmation(self, m3u8_playlist, index):
        m3u8_obj = m3u8.load(m3u8_playlist)
        variant_info_dict = {}
        bandwidth_list = []
        if m3u8_obj.is_variant:
            for playlist in m3u8_obj.playlists:
                variant_info_dict[playlist.stream_info.bandwidth] = playlist.uri
                bandwidth_list.append(playlist.stream_info.bandwidth)

        final_bandwidth = max(bandwidth_list)
        true_m3u8_playlist = variant_info_dict[final_bandwidth]
        # print(true_m3u8_playlist)
        response = requests.get(true_m3u8_playlist, headers=self.headers)
        with open("index_{}.m3u8".format(index), "wb") as f:
            f.write(response.content)
            f.close()
        return true_m3u8_playlist

    def run(self):
        video_info_url, bj_name = self.get_video_info_url()
        self.login_in()
        m3u8_playlist_list = self.get_all_playlist(video_info_url)
        print("Downloading All {} segments.".format(len(m3u8_playlist_list)))
        video_name = self.get_video_name(bj_name)

        streaming_list = {}
        index = 1
        for m3u8_playlist in m3u8_playlist_list:
            true_m3u8_playlist = self.resolution_confirmation(m3u8_playlist, index)
            if len(m3u8_playlist_list) == 1:
                streaming_part_name = video_name + '.mp4'
            else:
                streaming_part_name = video_name + '_' + str(index) + '.mp4'
            index += 1
            streaming_list[streaming_part_name] = true_m3u8_playlist

        return streaming_list
