import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
from bs4 import BeautifulSoup
import models 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signin.db'
app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/css'
db = SQLAlchemy(app)
registered_user = None
searchbar = []

@app.route("/")
def main():
    global registered_user
    contents = db.session.query(models.Contents).all()

    Subsections = db.session.query(models.Contents.subsection).distinct()


    mostpopular = db.session.query(models.Rating).order_by(
        models.Rating.rating.desc()).limit(4).all()
    popular = []
    for news in mostpopular:
        query = db.session.query(models.Contents).filter_by(
            id=news.contents_id).first()
        popular.append(query)

    latest = db.session.query(models.Contents).order_by(
        models.Contents.id.desc()).limit(4).all()

    if registered_user is None:
        return render_template('homepage.html', contents=contents, subsection=Subsections, mostpopular=popular, latest=latest, searchbar=searchbar)
    else:
        bookmarks = db.session.query(models.Bookmark).filter_by(
            user_id=registered_user.id)
        return render_template('homepage.html', name=registered_user.username, contents=contents, subsection=Subsections, bookmark=bookmarks, mostpopular=popular, latest=latest, searchbar=searchbar)


@app.route("/subsection/<section>")
def subsection(section):
    Subsections = db.session.query(models.Contents.subsection).distinct()
    contents = db.session.query(models.Contents).filter_by(subsection=section).all()
    return render_template('section1.html', contents=contents, section=section, subsection=Subsections)

@app.route("/subsec/<news>")
def subsec(news):
    news = db.session.query(models.Contents).filter_by(Title=news).first()
    rating = db.session.query(models.Rating).filter_by(contents_id=news.id)
    temp = 0.0
    count = 0.0
    for r in rating:
        count += 1
        temp = r.rating + temp
        db.session.delete(r)
    if(count != 0):
        temp = temp / count
        query = models.Rating(temp, news.id)
        db.session.add(query)
        db.session.commit()

    imagac = news.images.split(";")
    print(imagac)
    imagac = imagac[:-1]
    for im in imagac:
        print(im)

    Subsections = db.session.query(models.Contents.subsection).distinct()
    comments = db.session.query(models.Comment).filter_by(contents_id=news.id)
    return render_template('subsec.html', rating=temp, comments=comments, news=news, imagac=imagac,subsection=Subsections)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global registered_user
    if request.method == 'GET':
        if registered_user is None:
            return render_template('login.html')
        else:
            # leads to already logedin
            return redirect(url_for('main'))

    username = request.form['uname']
    password = request.form['psw']

    print(password)
    
    registered_user = db.session.query(
        models.User).filter_by(username=username).first()

    if registered_user is not None:
        status = sha256_crypt.verify(password, registered_user.password)

    if registered_user is None:
        return '<h2/>Invalid Login !! Try again !<a href="http://localhost:5000/signup" style="text-decoration:None"> Click here to signup again</a>'
        
    if status:
        registered_user.active = True
        return redirect(url_for('main'))
    else:
        registered_user = None
        return '<h2/>Invalid Login !! Try again !<a href="http://localhost:5000/login" style="text-decoration:None"> Click here to login again</a>'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global registered_user

    if request.method == 'GET':
        if registered_user is None:
            return render_template('signup.html')
        else:
            return redirect(url_for('main'))

    name = db.session.query(models.User).filter_by(
        username=request.form['username']).first()
    if request.form['psw'] == request.form['psw-repeat'] and name is None:
        password = request.form['psw']
        password = sha256_crypt.hash(password)
        user = models.User(request.form['username'], password,
                    request.form['psw-repeat'], "")
        username = user.username
        password = user.password
        print(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        if request.form['psw'] != request.form['psw-repeat']:
            return '<h2/> The passwords you entered did not match ! Please try again !<a href="http://localhost:5000/signup" style="text-decoration:None"> Click here to signup again</a>'
        elif name is not None:
            return '<h2/> Sorry! Username already taken<a href="http://localhost:5000/signup" style="text-decoration:None"> Click here to signup again</a>'


@app.route('/logout')
def logout():
    global registered_user
    if registered_user is None:
        return redirect(url_for('main'))

    else:
        registered_user.user_logout()
        registered_user = None
        return render_template('logout.html')


@app.route('/adminadd', methods=['Get', 'POST'])
def adminadd():
    global registered_user

    if request.method == 'GET':
        if(registered_user == None or registered_user.username != "admin"):
            return redirect(url_for('main'))
        else:
            return render_template('admin.html')

    if registered_user is None:
        return redirect(url_for('login'))
    else:
        if registered_user.username == "admin":
            content = request.form['content']
            soup = BeautifulSoup(content)
            content = soup.text
            image = request.files['image']
            img = soup.find_all("img")

            imgac = ""
            for i in img:
                print(i.get("src"))
                imgac += i.get("src") + ";"
            subsection = request.form['subsection']
            title = request.form['Title']
            image = request.files['image']
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOADS_FOLDER'], filename))
            contents = models.Contents(content, subsection, title,
                                '0', filename, imgac)
            db.session.add(contents)
            db.session.commit()
        return redirect(url_for('main'))


@app.route('/admindelete', methods=['POST', 'GET'])
def admindelete():
    if request.method == 'GET':
        return redirect(url_for('main'))

    query = db.session.query(models.Contents).filter_by(
        Title=request.form['Title']).first()
    if query is not None:
        db.session.delete(query)
        db.session.commit()
        return redirect(url_for('main'))
    else:
        return '<h2>SORRY NO SUCH CONTENT IS AVAILABLE!!!</h2>'


@app.route('/adminupdate', methods=['POST', 'GET'])
def adminupdate():
    if request.method == 'GET':
        return redirect(url_for('main'))

    title = request.form['Title']
    if title is None:
        return '<h2>SORRY NO SUCH CONTENT IS AVAILABLE!!!</h2>'
    else:
        query = db.session.query(models.Contents).filter_by(Title=title).first()
        return render_template('admin.html', title=query)


@app.route('/adminmodify', methods=['POST', 'GET'])
def adminmodify():
    if request.method == 'GET':
        return redirect(url_for('main'))
    else:
        title = request.form['Title']
        query = db.session.query(models.Contents).filter_by(Title=title).first()
        query.newscontent = request.form['content']
        query.Title = request.form['Title']
        db.session.commit()
        return redirect(url_for('main'))


@app.route('/rating/<news>', methods=['Get', 'POST'])
def rating(news):
    global registered_user
    if registered_user is None:
        return redirect(url_for('signup'))


    query = db.session.query(models.Contents).filter_by(Title=news).first()
    if request.method == 'GET':
        return redirect(url_for('subsec', news=news))
    else:
        if str(query.id) not in registered_user.ratelist:
            registered_user.ratelist += str(query.id) + ";"
            rating = request.form['rating']
            ratings = models.Rating(rating, query.id)
            db.session.add(ratings)
            db.session.commit()
    return redirect(url_for('subsec', news=news))


@app.route('/comment/<news>', methods=['Get', 'POST'])
def comment(news):
    global registered_user
    if registered_user is None:
        return redirect(url_for('signup'))

    query = db.session.query(models.Contents).filter_by(Title=news).first()
    if request.method == 'GET':
        return redirect(url_for('subsec', news=news))
    else:
        comm = request.form['comment']
        comments = models.Comment(comm, registered_user.username, query.id)
        db.session.add(comments)
        db.session.commit()
    return redirect(url_for('subsec', news=news))


@app.route('/bookmark', methods=['POST'])
def bookmark():
    global registered_user
    if registered_user is None:
        return redirect(url_for('signup'))

    book = request.form['bookmark']
    bookmark = models.Bookmark(book, registered_user.id)
    db.session.add(bookmark)
    db.session.commit()
    return redirect(url_for('subsec', news=book))


@app.route('/search', methods=['POST'])
def search():
    global searchbar
    searchbar = []
    search1 = request.form['search']
    search1 = db.session.query(models.Contents).filter(
        models.Contents.Title.ilike("%" + search1 + "%")).all()
    for s in search1:
        searchbar.append(s)

    return redirect(url_for('main'))


@app.errorhandler(404)
def page_error(error):
    return '<h2/>Sorry! The requested resource could not be found but maybe available in the future :('


@app.errorhandler(400)
def page_error(error):
    return '<h2/>Sorry! The server cannot or will not process the request due to an apparent client error :('


if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()
#   app.run(ssl_context=('cert.pem', 'key.pem'))
