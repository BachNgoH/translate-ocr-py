import os
from flask import Flask, request, session
import flask_cors
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import logging
import easyocr
import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("HELLO WORLD")
UPLOAD_FOLDER = '/tmp/to/the/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

flask_cors.CORS(app, resources='/api/*')

tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")

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
  file = request.files['voice']
  print(file)
  print(file.filename)
  filename = secure_filename(file.filename)
  destination = "/".join([target, filename])
  file.save(destination)
  session['uploadFilePath']=destination

  r = sr.Recognizer()

  recording = sr.AudioFile(file)
  with recording as source:
      audio = r.record(source)

  text = r.recognize_google(audio)
  
  return  {"resultText": text}

@app.route('/api/summarize', methods=['POST'])
def summarize():
  text = request.form['text']
  mode = request.form['mode']

  if mode == 'abstractive':

    inputs = tokenizer.batch_encode_plus([text], return_tensors='pt',max_length=64)
    summary_ids=model.generate(inputs['input_ids'], early_stopping=True)

    summary=tokenizer.decode(summary_ids[0],skip_special_tokens=True)

  if mode == 'extractive':
    my_parser = PlaintextParser.from_string(text, Tokenizer('english'))
    lex_rank_summarizer = LexRankSummarizer()
    lexrank_summary = lex_rank_summarizer(my_parser.document, sentences_count=3)
    tmp_summary = []
    for sentence in lexrank_summary:
      print(sentence)
      tmp_summary.append(str(sentence))
    summary = " ".join( tmp_summary )

  print(summary)
  print(type(summary))
  return {"summary": summary}

@app.route('/')
def index():
  return "<h1>Welcome to CodingX</h1>"


# CORS(app, expose_headers='Authorization')