import magic
import time
from AudioProject import AudioProject
from mutagen import mp3, wave
import io
#import json


class AudioHandler:
    def __init__(self):
        self.storage = {}

    def __putAudio(self, key, audioData):
        if (key in self.storage):
            raise Exception("Key already exists")
        if (key is None):
            key = str(time.time_ns())
        audioProject = AudioProject(audioData, key)
        self.storage[key] = audioProject
        return key

    def __recordMatchesCriteria(self,recordKey,criteria):
        audioProject = self.storage[recordKey]
        if ('maxduration' in criteria):
            if(int(criteria['maxduration']) < int(audioProject.length)):
                return False
        if ('minduration' in criteria):
            if (int(criteria['minduration']) > int(audioProject.length)):
                return False
        if ('mime' in criteria):
            if (criteria['mime'] != audioProject.mime):
                return False
        if ('namecontains' in criteria):
            if (str(criteria['namecontains']) not in recordKey):
                return False
        if ('name' in criteria):
            if (str(criteria['name']) != recordKey):
                return False
        return True

    ########## Public Methods ##########

    def storeAudioBytes(self, data, fileName = None):
        data = data.read()
        return self.__putAudio(fileName, data)

    def getData(self, fileName):
        if not self.fileExists(fileName):
            raise FileNotFoundError
        return self.storage[fileName]

    def fileExists(self, fileName):
        return fileName in self.storage.keys()

    def searchForFiles(self, criteria):
        ret = {
            'storedData':[],
            'storeCount': 0
        }
        for key in self.storage.keys():
            if (self.__recordMatchesCriteria(key,criteria)):
                metaData = {}
                metaData['name'] = key
                metaData['length'] = self.storage[key].length
                metaData['mime'] = self.storage[key].mime
                ret['storedData'].append(metaData)
        ret['storeCount'] = len(ret['storedData'])
        return ret
