import uuid
import json
class User():
    def __init__(self, publicID, name, password):
        self.__id = uuid.uuid4()
        self.__publicID = publicID
        self.__name = name
        self.__password = password

    def __repr__(self):
        return json.dumps({
            "UUID" : str(self.__id),
            "publicID" : self.__publicID,
            "name" : self.__name,
            "password" : self.__password
        })

    def getName(self):
        return self.__name

    def getPublicID(self):
        return self.__publicID

    def getPasswordHash(self):
        return self.__password

    def getUUID(self):
        return self.__id