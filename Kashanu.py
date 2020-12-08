#
#  Ali Fallah (c) 2020 December
# Adobe Connect Converter
#

import urllib
import time
import requests
import re
from ConnectToMP4 import adobe_connect_to_mp4 

class KashanUniversity:
    def __init__(self):
        self.session = requests.Session()
        self.adobe_url = ""
        self.ـlogout_url = ""
        pass

    def login(self,url,username,password):
        def change_sesskey(url,sesskey):
            parsed_url = urllib.parse.urlparse(url)
            query = dict(urllib.parse.parse_qsl(parsed_url.query))
            query['sesskey'] = sesskey
            query = urllib.parse.urlencode(query)
            parsed_url_dict = list(parsed_url)
            parsed_url_dict[4] = query
            final_url = urllib.parse.urlunparse(tuple(parsed_url_dict))
            return final_url
        self.session.headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://lms.kashanu.ac.ir',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://lms.kashanu.ac.ir/login/index.php',
        'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
        }
        indexpage = self.session.get("http://lms.kashanu.ac.ir")   
        logintoken = re.findall(r'<input type="hidden" name="logintoken" value="(.*)">',indexpage.text)[0]
        payload=f'anchor=&logintoken={logintoken}&username={username}&password={password}'
        response = self.session.post("http://lms.kashanu.ac.ir/login/index.php",data=payload)
        try:
            self.ـlogout_url,sesskey = re.findall(r'(http://lms.kashanu.ac.ir/login/logout.php\?sesskey=([^\s"]*))',response.text)[0]
        except:
            raise Exception("incorrect username or password")

        url = change_sesskey(url,sesskey)
        time.sleep(6)
        r = self.session.get(url) 
        self.adobe_url = r.url
        return self.adobe_url

    def logout(self):
        if self.ـlogout_url : 
            self.session.get(self.ـlogout_url)

    def get_adobe_url(self,url,username,password):
        adobe_url = self.login(url,username,password)
        return adobe_url

def record_adobe_kashanu(username,password,link):
    university = KashanUniversity()
    try:
        adobe_url = university.get_adobe_url(link,username,password)
        adobe_connect_to_mp4(adobe_url,".",100)
    except:
        raise
    finally:
        university.logout()

if __name__ == "__main__":
    ku_url = "http://lms.kashanu.ac.ir/mod/adobeconnect/joinrecording.php?id=14667&recording=11059668&groupid=0"
    username = "9721160031"
    password = "Password:)"
    record_adobe_kashanu(username,password,ku_url)