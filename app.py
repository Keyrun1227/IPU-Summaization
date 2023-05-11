import heapq
from flask import Flask, render_template, request, send_file, session
import bs4 as bs
import urllib.request
import os
import cv2
import pytesseract
import re
import nltk
from PyPDF2 import PdfReader
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)


def ocr_img(image):
    text = pytesseract.image_to_string(image)
    return text


UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
RESULT_FOLDER = 'static/results/'
app.config['RESULT_FOLDER'] = RESULT_FOLDER



@app.route('/')
def man():
    return render_template('index.html')


@app.route('/Url')
def url():
    return render_template('url.html')


@app.route('/Pdf')
def pdf():
    return render_template('pdf.html')


@app.route('/Image')
def image():
    return render_template('image.html')


@app.route('/download')
def download_file():
    path ="static/result/kiran.txt"
    return send_file(path, as_attachment=True)


@app.route('/pdf', methods=['POST'])
def komali():
    submit = request.form['cat']
    if request.method == "POST":
        n = int(request.form['a'])
        file = request.files.get('filename')
        if file is None:
            return "No file uploaded"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        if file:
            a = PdfReader(file)
            k = len(a.pages)
            str = ""
            for i in range(k):
                str += a.pages[i].extract_text()
            str = re.sub(r'\[[0-9]*\]', ' ', str)
            str = re.sub(r'\s+', ' ', str)
            formatted_article_text = re.sub('[^a-zA-Z]', ' ', str)
            formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
            sentence_list = nltk.sent_tokenize(str)
            stopwords = nltk.corpus.stopwords.words('english')
            word_frequencies = {}
            for word in nltk.word_tokenize(formatted_article_text):
                if word not in stopwords:
                    if word not in word_frequencies.keys():
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1
            max_frequency = max(word_frequencies.values())
            for word in word_frequencies.keys():
                word_frequencies[word] = (word_frequencies[word]/max_frequency)
            sentence_scores = {}
            for sent in sentence_list:
                for word in nltk.word_tokenize(sent.lower()):
                    if word in word_frequencies.keys():
                        if len(sent.split(' ')) < 30:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word]
                            else:
                                sentence_scores[sent] += word_frequencies[word]
            summary_sentences = heapq.nlargest(
                n, sentence_scores, key=sentence_scores.get)
            summary = ''.join(summary_sentences)
            if submit == 'summary':
                sol = summary
            elif submit == "sentence_list":
                sol = sentence_list
            elif submit == "text":
                sol = str
            elif submit == "formatted_at":
                sol = formatted_article_text
            elif submit == "stopwords":
                sol = stopwords
            else:
                sol = word_frequencies
            with open("static/result/kiran.txt", "w", encoding='utf-8') as f:
                f.truncate()
                f.write(sol)
                f.close()                
    return render_template('summary.html', data=sol)


@app.route('/image', methods=['GET', 'POST'])
def sai():
    submit = request.form['cat']
    if request.method == "POST":
        n = int(request.form['a'])
        file = request.files.get('filename')
        if file is None:
            return "No file uploaded"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        input_file = file.filename
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        img = cv2.imread(input_file)

        # convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # perform thresholding to remove noise
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # perform morphological operations to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        # extract text from image
        strs = ocr_img(opening)
        # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # ret, thresh1 = cv2.threshold(
        #     gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        # dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
        # contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
        #                                        cv2.CHAIN_APPROX_NONE)
        # im2 = img.copy()
        # file = open("recognized.txt", "w+")
        # file.write("")
        # file.close()
        # for cnt in contours:
        #     x, y, w, h = cv2.boundingRect(cnt)
        #     rect = cv2.rectangle(
        #         im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #     cropped = im2[y:y + h, x:x + w]
        #     file = open("recognized.txt", "a")
        #     text = pytesseract.image_to_string(cropped)
        #     file.write(text)
        #     file.write("\n")
        #     file.close
        #     file = open("recognized.txt", "r")
        #     read = file.readlines()
        #     modified = []
        #     for line in read:
        #         modified.append(line)
        #     modified.reverse()
        modified = re.sub(r'\[[0-9]*\]', ' ', strs)
        modified = re.sub(r'\s+', ' ', modified)
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', modified)
        formatted_article_text = re.sub(
            r'\s+', ' ', formatted_article_text)
        sentence_list = nltk.sent_tokenize(modified)
        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        max_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (
                word_frequencies[word]/max_frequency)

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        summary_sentences = heapq.nlargest(
            n, sentence_scores, key=sentence_scores.get)
        summary = ''.join(summary_sentences)
        if submit == 'summary':
            sol = summary
        elif submit == "sentence_list":
            sol = sentence_list
        elif submit == "text":
            sol = modified
        elif submit == "formatted_at":
            sol = formatted_article_text
        elif submit == "stopwords":
            sol = stopwords
        else:
            sol = word_frequencies
        with open("static/result/kiran.txt", "w", encoding='utf-8') as f:
            f.truncate()
            f.write(sol)
            f.close()
    return render_template('summary.html', data=sol)


@app.route('/summary', methods=['POST'])
def kiran():
    submit = request.form['cat']
    data = request.form['url']
    n = int(request.form['a'])
    scraped_data = urllib.request.urlopen(data)
    article = scraped_data.read()
    parsed_article = bs.BeautifulSoup(article, 'lxml')
    paragraphs = parsed_article.find_all('p')
    article_text = ""
    for p in paragraphs:
        article_text += p.text
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text)
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
    sentence_list = nltk.sent_tokenize(article_text)
    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/max_frequency)

    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(
        n, sentence_scores, key=sentence_scores.get)
    summary = ''.join(summary_sentences)
    if submit == 'summary':
        sol = summary
    elif submit == "sentence_list":
        sol = sentence_list
    elif submit == "text":
        sol = article_text
    elif submit == "formatted_at":
        sol = formatted_article_text
    elif submit == "stopwords":
        sol = stopwords
    else:
        sol = word_frequencies
    with open("static/result/kiran.txt", "w", encoding='utf-8') as f:
        f.truncate()
        f.write(sol)
        f.close()
        f.save(os.path.join(app.config['RESULT_FOLDER'], 'kiran.txt'))
    return render_template('summary.html', data=sol)


if __name__ == "__main__":
    app.run(debug=True)
