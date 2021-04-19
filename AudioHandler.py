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

    def __recordMatchesCriteriaAndUser(self,recordKey, criteria, UUID): # Could have used boolean logic here, but this seems easier to read
        audioProject = self.storage[recordKey]
        if (audioProject.getOwnerUUID() != UUID):
            return False
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

    def getAudioProject(self, fileName, ownerUUID):
        if fileName not in self.storage.keys():
            raise AudioFileNotFoundException
        audioProject = self.storage[fileName]
        if audioProject.getOwnerUUID() != ownerUUID:
            raise AudioFileNotFoundException
        return audioProject

    def searchForFiles(self, criteria, ownerUUID):
        ret = {
            'storedData':[],
            'count': 0
        }
        # Brute force search, this is not an issue though because, in practice, database queries will handle searching
        for key in self.storage.keys():
            if (self.__recordMatchesCriteriaAndUser(key,criteria, ownerUUID)):
                metaData = {}
                metaData['name'] = key
                metaData['length'] = self.storage[key].getLength()
                metaData['mime'] = self.storage[key].getMime()
                ret['storedData'].append(metaData)
        ret['count'] = len(ret['storedData'])
        return ret
