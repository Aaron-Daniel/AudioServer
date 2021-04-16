from flask import Flask, request, send_file, jsonify
import traceback
from gevent.pywsgi import WSGIServer
import io
import json
from AudioHandler import AudioHandler
from Authentication.Authenticator import Authenticator
from Authentication.AuthExceptions import TokenVerificationException
# flask and server
app = Flask(__name__)
server = None

# initialize backend
audioHandler = AudioHandler()
authHandler = Authenticator()

################# Test Routes #################
@app.route('/ping', methods=['GET'])
def ping():
    return 'PONG', 200


@app.route('/', methods=['GET'])
def index():
    return ping()

################# Audio Routes #################
@app.route('/upload', methods=['POST'])
@authHandler.tokenRequired
def uploadAudioStream(authenticatedUser):
    try:
        data = request.stream
        fileName = request.args.get('filename')
        audioHandler.storeAudioBytes(data, authenticatedUser.getUUID(), fileName=fileName)
        return "Created", 201
    except:
        tb = str(traceback.format_exc())
        print(tb)
        return jsonify({"message": "upload failed"}), 500


@app.route('/download', methods=['GET'])
def downloadAudio(authenticatedUser):
    fileName = request.args.get('name')
    if fileName is None:
        return "No file specified", 500
    if not audioHandler.fileExists(fileName):
        return "File Not Found", 404
    fileData = audioHandler.getAudioProject(fileName)
    audioData = fileData.getData()
    mime = fileData.getMime()
    ret = io.BytesIO()
    ret.write(audioData)
    ret.seek(0)
    try:
        return send_file(ret, mimetype=mime), 200
    except:
        return jsonify({"message": "download failed"}), 500


@app.route('/list', methods=['GET'])
@authHandler.tokenRequired
def lstAudio(authenticatedUser):
    criteria = {}
    for arg in ['maxduration', 'minduration', 'mime', 'namecontains', 'name']:
        if (request.args.get(arg) is not None):
            criteria[arg] = request.args.get(arg)
    return audioHandler.searchForFiles(criteria), 200

'''It was unclear how this differs from /list so I simply implemented it with similar logic to fit the
 requirement'''
@app.route('/info', methods=['GET'])
@authHandler.tokenRequired
def getAudioInfo(authenticatedUser):
    nameparam = request.args.get('name')
    if nameparam is not None:
        res = audioHandler.searchForFiles({'name':nameparam})
        if (res['storeCount'] > 1):
            return jsonify({"message" : "Something went wrong"}), 500
        if (res['storeCount'] < 1):
            return jsonify({"message" : "File Not Found"}) , 404
        return json.dumps(res), 200
    return {}, 200

################# Authentication Routes #################
@app.route('/register',methods=['POST'])
def signupUser():
    data = request.get_json()
    if data is None or data['password'] is None or data['publicID'] is None or data['name'] is None:
        return jsonify({"message" : "invalid headers, please provide: password, publicID, name"})
    user = authHandler.createNewUser(data)
    return jsonify({"message" : "created"}), 201

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message':'invalid token'}), 401
    try:
        token = authHandler.login(auth)
        return jsonify({'token': token.decode('UTF-8')})
    except TokenVerificationException:
        return jsonify({'message':'token verification failed'}), 401

    ################# Init Server #################

if __name__ == '__main__':
    # set up and run server
    # handleArgumentInputs(sys.argv[1:])
    server = WSGIServer(('0.0.0.0', int(8080)), app)
    try:
        print("Server is ready...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server Stopped")
    server.close()
