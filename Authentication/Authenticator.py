from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from Authentication.AuthExceptions import *

from functools import wraps
from Authentication.User import User

import traceback

class Authenticator:

    def __init__(self):
        self.__SECRET_KEY = 'Th1s1ss3cr3t'
        self.__usersDB = {}

    def __storeUser(self, user):
        if (user.getPublicID() in self.__usersDB):
            raise UserAlreadyExistsException('User Already Exists')
        self.__usersDB[user.getPublicID()] = user
        return user

    def __getUser(self, publicID):
        if (publicID not in self.__usersDB):
            raise UserNotFoundException()
        return self.__usersDB[publicID]

    ########## Public Methods ##########

    def createNewUser(self, data):
        hashedPassword = generate_password_hash(data['password'], method='sha256')
        newUser = User(data['publicID'], data['name'], hashedPassword)
        self.__storeUser(newUser)
        return newUser

    def login(self, auth):
        user = self.__getUser(auth.username)
        #print(user)
        if check_password_hash(user.getPasswordHash(), auth.password):
            token = jwt.encode(
                {
                "publicID": user.getPublicID(),
                "expiration": (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).strftime("%m/%d/%Y, %H:%M:%S")
                },
                self.__SECRET_KEY)
            return token
        raise TokenVerificationException

    def tokenRequired(self, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']
            if not token:
                return jsonify({'message': 'a valid token is missing'}), 401
            try:
                data = jwt.decode(token, self.__SECRET_KEY)
                current_user = self.__usersDB[data['publicID']]
            except:
                print(traceback.format_exc())
                return jsonify({'message': 'token is invalid'}), 401
            return f(current_user, *args, **kwargs)
        return decorator




