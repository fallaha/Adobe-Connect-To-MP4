#
#  Ali Fallah (c) 2020 December
# Adobe Connect Converter
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import subprocess, shlex
from xvfbwrapper import Xvfb
import os
from ConnectToMP3 import AdobeConnectToMP3
import  requests
import urllib
import re
import time
from collections import namedtuple



def adobe_connect_to_mp4(classroom_link,directory_path,duration=0):
    """
    This Function Get Adobe Connect Link and Download Adobe Zip file
    Convert it to MP3 and then Open class in Firefox with Selenium
    and record Screen without Sound by FFMPEG and in the end of function
    merege audio and video to make a mp4 file
    """
    def get_classid_(url):
        '''
        parse URL and determine Meeting ID.
        '''
        try:
            o = urllib.parse.urlparse(url)
            classroomid = (o.path[1:].split('/'))[0] # get classroom id
            return classroomid
        except:
            raise Exception("Your Adobe Link is not a correct URL for a meeting")


    classroom_id = get_classid_(classroom_link)

    def manage_path(directory_path):
        """
        this function define path that needing in function
        """
        absdir_path = os.path.join(os.path.abspath(directory_path),classroom_id)
        path = namedtuple('Path',['dir','zip','video','audio','midvideo','output'])\
                    (absdir_path,
                    os.path.join(absdir_path,classroom_id+'.zip'),
                    os.path.join(absdir_path,"video.mkv"),
                    os.path.join(absdir_path,"audio.mp3"),
                    os.path.join(absdir_path,"video.mkv"),
                    os.path.join(absdir_path,classroom_id+".mp4"),
                    )
        os.makedirs(path.dir,exist_ok=True)
        return path

    path = manage_path(directory_path)

    def download_zip_file(url,download_path):
        def get_zip_file_url(url):
            o = urllib.parse.urlparse(url)
            query = dict(urllib.parse.parse_qsl(o.query))
            query['download'] = 'zip'
            parsed_url = list(o)
            parsed_url[2] = parsed_url[2]+"output/raw.zip"
            parsed_url[4] = urllib.parse.urlencode(query)
            return urllib.parse.urlunparse(tuple(parsed_url))

        if os.path.isfile(download_path): return
        zip_url = get_zip_file_url(url)
        r = requests.get(zip_url)
        with open(download_path, 'wb') as f:
            f.write(r.content)
            
    download_zip_file(classroom_link,path.zip)
    mp3 = AdobeConnectToMP3(path.zip)
    mp3.convert_sync()
    print("mp3 Converted")
    
    # Start Recording Class

    xvfb = Xvfb(width=1280, height=720, colordepth=24)
    xvfb.start()
    os.environ["DISPLAY"] = ":"+str(xvfb.new_display)
    import pyautogui

    # initialize firefox browser
    fp = FirefoxProfile()
    options = Options()
    options.add_argument("--width=1280")
    options.add_argument("--height=794")
    fp.set_preference("plugin.state.flash",2)
    fp.set_preference("dom.ipc.plugins.enabled.libflashplayer.so","true")
    browser = webdriver.Firefox(firefox_profile=fp,options=options)
    browser.set_window_position(0,-74)


    ffmpeg_stream = 'ffmpeg -y -r 30 -framerate 25 -f x11grab -draw_mouse 0 -s 1280x720  -i :%d %s' % (xvfb.new_display, path.midvideo)

    print("Display Number is :"+str(xvfb.new_display))
    print("cmd command : "+ffmpeg_stream)
    browser.get(classroom_link)

    timeout_cntr = 40
    while not pyautogui.pixelMatchesColor(1200, 700,(216,216,216)):
        time.sleep(0.5)
        timeout_cntr -= 1
        if not timeout_cntr:
            browser.quit()
            xvfb.stop()
            raise Exception("an Error Occurred when try to Connect to Metting")

    print("enter to class successfullly")

    args = shlex.split(ffmpeg_stream)
    p = subprocess.Popen(args)

    if duration == 0: duration = mp3.duration
    time.sleep(duration) # record for <duration> secs
    p.terminate()
    browser.quit()
    xvfb.stop()

    print("screen capture finished")

    # merage mkv and mp3 to mp4
    ffmpeg_cmd = f"ffmpeg -y -an -i {path.video} -vn -i {path.audio} -c:v copy -c:a aac -shortest {path.output}"
    args = shlex.split(ffmpeg_cmd)
    p = subprocess.Popen(args).wait()
    print("Every Thing done successfully.")


