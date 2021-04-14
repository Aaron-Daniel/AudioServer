from flask import Flask, request, send_file
import traceback
from gevent.pywsgi import WSGIServer
import io
import json
from AudioHandler import AudioHandler

# flask and server
app = Flask(__name__)
server = None

# initialize backend
audioHandler = AudioHandler()


@app.route('/ping', methods=['GET'])
def ping():
    return 'PONG', 200


@app.route('/', methods=['GET'])
def index():
    return ping()


@app.route('/upload', methods=['POST'])
def uploadAudioStream():
    try:
        data = request.stream
        fileName = None
        if("filename" in request.headers):
            fileName = request.headers["filename"]
        key = audioHandler.storeAudioBytes(data, fileName=fileName)
        return "Created", 201
    except:
        tb = str(traceback.format_exc())
        print(tb)
        return "Failed", 500


@app.route('/download', methods=['GET'])
def downloadAudio():
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
        return 'download failed', 500


@app.route('/list', methods=['GET'])
def lstAudio():
    criteria = {}
    for arg in ['maxduration', 'minduration', 'mime', 'namecontains', 'name']:
        if (request.args.get(arg) is not None):
            criteria[arg] = request.args.get(arg)
    return audioHandler.searchForFiles(criteria), 200

'''It was unclear how this differs from /list so I simply implemented it with similar logic to fit the
 requirement'''
@app.route('/info', methods=['GET'])
def getAudioInfo():
    nameparam = request.args.get('name')
    if nameparam is not None:
        res = audioHandler.searchForFiles({'name':nameparam})
        if (res['storeCount'] > 1):
            raise Exception('Too many files')
        if (res['storeCount'] < 1):
            return "File Not Found", 404
        return json.dumps(res), 200
    return {}, 200


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
