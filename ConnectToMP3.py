#
#  Ali Fallah (c) 2020 December
#  Thanks to Mohammad Mehdi Rahimi
# Adobe Connect Converter
#


import zipfile
import os
import subprocess
import shlex
import xml.etree.ElementTree as ET
import threading

class AdobeConnectToMP3:
    """
    This Class Get a Path to ZIP File and Convert it To an mp3 file
    also has this.duration to detrmain classroom duration.
    """
    def __init__(self,zip_path):
        self._zip_path = zip_path
        self._dir_path = os.path.dirname(self._zip_path)
        self._raw_path = os.path.join(self._dir_path,"raw")
        self.duration = 0
        self.audios = []

    def _extract_zip(self):
        with zipfile.ZipFile(self._zip_path,'r') as zip_ref:
            zip_ref.extractall(self._raw_path)

    def _get_duration_and_audios_objs(self):
        finalizeTime=False
        main_stream_xml_path = os.path.join(self._raw_path,"mainstream.xml")
        tree = ET.parse(main_stream_xml_path)
        root = tree.getroot()

        nextInvisted = False
        for child in root:
            if finalizeTime == False:
                totalTime = child.attrib
            for childChild in child:
                if nextInvisted and childChild.tag=="Array":

                    for myObject in childChild.findall('Object'):
                        startTime = myObject.find("startTime").text
                        name = myObject.find("streamName").text
                        tempDict={"name":name,"startTime":int(startTime)//1000}
                        self.audios.append(tempDict)
                    nextInvisted=False
                if childChild.tag=="String" and childChild.text=="streamAdded" :
                    nextInvisted =True  #next one tag should be visited becaus condition are hold
                if childChild.tag == "String":
                    if childChild.text == "__stop__":
                        finalizeTime=True
        self.duration = int(totalTime["time"])//1000
   
    def _get_ffmpeg_command(self):
        command = ["-itsoffset %i -i %s.flv" %(item["startTime"],os.path.join(self._raw_path,item['name'][1:])) for item in self.audios]
        ffmpeg_cmd = """ffmpeg -y {0}\
        -filter_complex "amix=inputs={1}:duration=longest [aout]" -map [aout] -acodec mp3 \
        -async 1 -t {2} {3}""".format(" ".join(command),str(len(self.audios)),self.duration,os.path.join(self._dir_path,"audio.mp3"))

        if os.name == "nt": 
            ffmpeg_cmd = ffmpeg_cmd.replace('\\','\\\\')

        return ffmpeg_cmd

    def convert(self,onsuccess=None,onfail=None):
        self._extract_zip()
        self._get_duration_and_audios_objs()
        cmd = self._get_ffmpeg_command()

        def run_command(onsuccess=None,onfail=None):
            args = shlex.split(cmd)
            p = subprocess.Popen(args).wait()
            if not p:
                if onsuccess: onsuccess(self)
            else:
                if onfail: onfail(self)

        t = threading.Thread(target=run_command,kwargs={"onsuccess":onsuccess,"onfail":onfail})
        t.start()
        return cmd

    def convert_sync(self):
        self._extract_zip()
        self._get_duration_and_audios_objs()
        if os.path.isfile(os.path.join(self._dir_path,"audio.mp3")):
            return
        cmd = self._get_ffmpeg_command()

        args = shlex.split(cmd)
        p = subprocess.Popen(args).wait()
        return p

