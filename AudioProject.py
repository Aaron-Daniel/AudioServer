import magic
from mutagen import mp3, wave
import io

class AudioProject:
    def __init__(self, audioData, name):
        self.mime = None
        self.name = name
        self.length = None
        self.supportedAudioTypes = ['wav', 'mpeg']
        self.data = audioData
        self.__detectAudioType()
        self.__getAudioLengthFromBytes() #getAudioLength must go after detectAudioType

    def __detectAudioType(self):
        dataHead = self.data[:1024]
        mime = magic.from_buffer(dataHead, mime=True)
        if not mime.startswith("audio"):
            raise Exception("Data must be Audio")
        dataType = mime[6:]
        if dataType.lower() not in self.supportedAudioTypes:
            raise Exception("Unsupported Audio Format")
        self.mime = mime

    def __validateAudioDataType(self):
        dataHead = self.data[:1024]
        mime = magic.from_buffer(dataHead, mime=True)
        return mime.startswith("audio")

    def __getAudioLengthFromBytes(self):
        audio = ""
        try:
            if (self.mime.endswith("mpeg")):
                audio = mp3.MP3(io.BytesIO(self.data))
            elif (self.mime.endswith('wav')):
                audio = wave.WAVE(io.BytesIO(self.data))
        except:
            raise Exception("Audio Format Detection Failure")
        self.length = audio.info.length

    def getAudio(self):
        return self.data


    def getMime(self):
        return self.mime


    def getLength(self):
        return self.length

