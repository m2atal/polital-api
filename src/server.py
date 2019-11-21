import pdftotext
from stop_words import get_stop_words
from flask import Flask, request, jsonify
from multi_rake import Rake
from gensim.summarization.summarizer import summarize

ALLOWED_EXTENSIONS = set(['pdf'])
KEYWORDS_COUNT     = 15
SUMMARY_COUNT      = 500

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

sw   = set(get_stop_words('fr'))
rake = Rake(language_code='fr', stopwords=sw, min_freq=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        pdf = pdftotext.PDF(file)
        text = "\n".join(pdf)
        text = text.replace('\n', ' ')
        keywords_text = [kw[0] for kw in rake.apply(text.lower())[:KEYWORDS_COUNT]]
        summary_text  = ". ".join(summarize(text, word_count=SUMMARY_COUNT, split=True))

        resp = jsonify({
            'keywords': keywords_text,
            'summary':  summary_text
        })
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


if __name__ == '__main__':
    app.run()
