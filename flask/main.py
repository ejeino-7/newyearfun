# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import os
import random


app = Flask(__name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    try:
        if session['logged_in'] == True:
            return render_template('/index.html')
        else:
            return redirect(url_for('login'))
    except KeyError:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        arr = []
        f = open(UPLOAD_FOLDER + 'users.txt', 'r+')

        line = f.readline()
        while line != "--":
            line = line.replace('\n', '')
            split = line.split(';')
            arr.append(split)
            line = f.readline()
        f.close()
               
        for user in arr:
            if user[0] == username and user[1] == password:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
                                                            
    return render_template('/login.html')

 
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
    
# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap




@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image'] 

        filename = str(session['username']) + "_" + name + ".png"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/images/", filename))
        
        f = open(UPLOAD_FOLDER + 'urls.txt', 'r+')
        content = ""
        line = f.readline()
        while line != "":
            content += line
            line = f.readline()
        
        new = filename + ";\n" + content
        
        f.truncate(0)
        f.seek(0)
        f.write(new)
        f.close()
        
        return redirect(url_for('index'))
    
    return render_template('upload.html')



@app.route('/play/<string:id>')
def play(id):
    try:
        if session['username'] == "admin":
            content_urls = []    
            
            f = open(UPLOAD_FOLDER + 'urls.txt', 'r')
            line = f.readline()
            while line != "":
                content_urls.append(line.split(";")[0])
                line = f.readline()
            f.close()
            
            content = []
            
            random.seed(int(id))
            random.shuffle(content_urls)

            i = 1
            for url in content_urls:
                dic = {'url': url, 'num': i}
                content.append(dic)
                i += 1
            return render_template('play.html', content=content)
        else:
            return '<h1> Sorry, only admin can start the game </h1>'
            
    except KeyError:
        return redirect(url_for('index'))

    
@app.route('/upload_words', methods=['GET', 'POST'])
def upload_words():
    if request.method == 'POST':
        word = request.form['word']

        f = open(UPLOAD_FOLDER + 'words.txt', 'r+')
        line = f.readline()
        
        new = word + ";" + line
        
        f.truncate(0)
        f.seek(0)
        f.write(new)
        f.close()
        
        return redirect(url_for('index'))
    
    return render_template('upload_words.html')    
    
    
@app.route('/play_words/<string:id>/<string:active>')
def play_words(id, active):
    try:
        if session['username'] == "admin":
            f = open(UPLOAD_FOLDER + 'words.txt', 'r')
            line = f.readline()
            f.close()
            words = line.split(';')
    
            random.seed(int(id))
            random.shuffle(words)
            
            content = []
            i = 1
            for word in words:
                dic = {'word': word, 'num': i}
                content.append(dic)
                i += 1
                
            if int(active) < len(content):
                return render_template('play_words.html', content=content, id=int(id), active=int(active) )
            else:
                return '<link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css\"><h1> Sorry, end of game </h1><div><button class=\"btn btn-primary\" onclick=\"location.href=\'/\'\">Home</button></div>'
        else:
            return '<h1> Sorry, only admin can start the game </h1>'
            
    except KeyError:
        return redirect(url_for('index'))
    
    
    
if __name__ == '__main__':
    app.secret_key = 'THISISTHEKEY'
    app.run(debug=True, host="0.0.0.0")