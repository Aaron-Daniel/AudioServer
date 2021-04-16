import time
from AudioHandlerExceptions import *
from AudioProject import AudioProject


class AudioHandler:
    def __init__(self):
        self.storage = {}

    def __putAudio(self, key, audioData, UUID):
        if (key in self.storage):
            raise KeyAlreadyExistsException
        if (key is None):
            key = str(time.time_ns())
        audioProject = AudioProject(audioData, key, UUID)
        self.storage[key] = audioProject
        return key

    def __recordMatchesCriteria(self,recordKey,criteria):
        audioProject = self.storage[recordKey]
        if ('maxduration' in criteria):
            if(int(criteria['maxduration']) < int(audioProject.getLength())):
                return False
        if ('minduration' in criteria):
            if (int(criteria['minduration']) > int(audioProject.getLength())):
                return False
        if ('mime' in criteria):
            if (criteria['mime'] != audioProject.getMime()):
                return False
        if ('namecontains' in criteria):
            if (str(criteria['namecontains']) not in recordKey):
                return False
        if ('name' in criteria):
            if (str(criteria['name']) != recordKey):
                return False
        return True

    ########## Public Methods ##########

    def storeAudioBytes(self, data, UUID, fileName = None):
        data = data.read()
        return self.__putAudio(fileName, data, UUID)

    def getAudioProject(self, fileName):
        if not self.fileExists(fileName):
            raise AudioFileNotFoundException
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
                metaData['length'] = self.storage[key].getLength()
                metaData['mime'] = self.storage[key].getMime()
                ret['storedData'].append(metaData)
        ret['storeCount'] = len(ret['storedData'])
        return ret
