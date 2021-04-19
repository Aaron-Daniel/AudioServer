import magic
from mutagen import mp3, wave
import io
from AudioHandlerExceptions import *

class AudioProject:
    def __init__(self, audioData, name, ownerUUID):
        self.__mime = None
        self.__name = name
        self.__length = None
        self.__supportedAudioTypes = ['wav', 'mpeg']
        self.__data = audioData
        self.__detectAudioType()
        self.__getAudioLengthFromBytes() #getAudioLength must run after detectAudioType
        self.__owner = ownerUUID

    def __repr__(self):
        return str(self.toDict())

    def __detectAudioType(self):
        dataHead = self.__data[:1024]
        mime = magic.from_buffer(dataHead, mime=True)
        if not mime.startswith("audio"):
            raise InvalidTypeException("Data must be Audio")
        dataType = mime[6:]
        if dataType.lower() not in self.__supportedAudioTypes:
            raise UnsupportedAudioFormatException
        self.__mime = mime

    def __validateAudioDataType(self):
        dataHead = self.__data[:1024]
        mime = magic.from_buffer(dataHead, mime=True)
        return mime.startswith("audio")

    def __getAudioLengthFromBytes(self):
        audio = ""
        try:
            if (self.__mime.endswith("mpeg")):
                audio = mp3.MP3(io.BytesIO(self.__data))
            elif (self.__mime.endswith('wav')):
                audio = wave.WAVE(io.BytesIO(self.__data))
        except:
            raise AudioFormatDetectionException("failed to detect audio format")
        self.__length = audio.info.length

    ########## Public Methods ##########

    def toDict(self):
        return {
            "name": self.__name,
            "length": self.__length,
            "mime": self.__mime
        }

    def getAudio(self):
        return self.__data

    def getMime(self):
        return self.__mime

    def getLength(self):
        return self.__length

    def getOwnerUUID(self):
        return self.__owner

