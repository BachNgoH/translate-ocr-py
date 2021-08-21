import os
from flask import Flask, request, session
import flask_cors
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import logging
import easyocr
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("HELLO WORLD")
UPLOAD_FOLDER = '/tmp/to/the/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

flask_cors.CORS(app, resources='/api/*')



def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-img', methods=['POST'])
def fileUpload():
  target = os.path.join(UPLOAD_FOLDER,'test_docs')
  if not os.path.isdir(target):
    os.makedirs(target)
  logger.info("welcome to upload")
  print(request)
  file = request.files['file']
  print(file)
  lang = request.form['lang']
  filename = secure_filename(file.filename)
  destination = "/".join([target, filename])
  file.save(destination)
  session['uploadFilePath']=destination

  print(lang)
  reader = easyocr.Reader([lang]) # need to run only once to load model into memory
  result = reader.readtext(destination)
  fulldoc = []
  #print(result)

  for res in result:
    fulldoc.append(res[1])
  
  resultText = " ".join(fulldoc)
  
  return  {"resultText": resultText}

@app.route('/api/upload-audio', methods=['POST'])
def audioUpload():
  target = os.path.join(UPLOAD_FOLDER,'test_docs')
  if not os.path.isdir(target):
    os.makedirs(target)
  logger.info("welcome to upload")
  file = request.files['file']
  print(file)
  filename = secure_filename(file.filename)
  destination = "/".join([target, filename])
  file.save(destination)
  session['uploadFilePath']=destination

  r = sr.Recognizer()

  recording = sr.AudioFile(destination)
  with recording as source:
      audio = r.record(source)

  text = r.recognize_google(audio)
  
  return  {"resultText": text}


@app.route('/')
def index():
  return "<h1>Welcome to CodingX</h1>"


# CORS(app, expose_headers='Authorization')