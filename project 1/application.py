import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json


app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
    #raise RuntimeError("DATABASE_URL is not set")

# onfigure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://jbgzwaswtepkqo:31b250316c82f24ff2508f0d20d5c23c985af44d5e2beebaf7c0eec0f1626bc3@ec2-174-129-255-91.compute-1.amazonaws.com:5432/d40tr17b3mpcf1')
db = scoped_session(sessionmaker(bind=engine))
@app.route("/", methods=['POST','GET'])
def singup():
    fname = request.form.get("fname")
    email = request.form.get("email")
    uname = request.form.get("uname")
    pwd = request.form.get("pwd")
    if "user_id" in session:
        return render_template("index.html")
    else:
        if request.method == "POST":
            data=db.execute("SELECT * FROM tbuser where username=:uname", {"uname":uname}).fetchall()
            if not data:
                db.execute("INSERT into tbuser(fullname,email,username,password) VALUES (:fname,:email,:username,:password)", {"fname":fname,"email":email,"username":uname,"password":pwd })
                db.commit()
                return render_template("login.html", message="Successfully registered.. fill your information here")
            else:
                return render_template("singup.html", message="User is allready taken try another one")
    return render_template("singup.html")
@app.route("/index",methods=['POST','GET'])
def index():
    if 'user_id' in session:
        if request.method == "POST":
            value = request.form.get("search")
            data = db.execute("SELECT * FROM book WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": '%' + value + '%',"title": '%' + value + '%',"author": '%' + value + '%'}).fetchall()
            if data is None:
                return render_template('index.html', message="Not FOund")
            else:
                return render_template('index.html', books=data)
        else:
            data = db.execute("SELECT * FROM book LIMIT 12").fetchall()
            if data is None:
                return render_template("index.html", message="No record is found")
            else:
                return render_template("index.html", books=data)
        return  render_template('index.html')
    else:
        return render_template("singup.html")
@app.route("/login", methods=['post','get'])
def login():
    if "user_id" in session:
        return render_template("index.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        data = db.execute("SELECT * FROM tbuser WHERE username=:uname AND password=:pwd", {"uname":username, "pwd":password}).fetchone()
        if not data:
            return render_template("login.html", message="Invalid Username or password")
        else:
            session["user_id"] = username
            session["uid"] = data['user_id']
            return redirect(url_for('index'))
    else:
        return render_template('login.html')
    return render_template("login.html")
@app.route("/review/<bisbn>/<bookid>", methods=['GET','POST'])
def review(bisbn,bookid):
    if 'user_id' in session:
        data=db.execute("select * from book where isbn=:bisbn", {"bisbn":bisbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"VepSePAnk5kkD2vOLcw", "isbns": bisbn})
        ratingNum = res.json()['books'][0].get('work_ratings_count')
        ratingAvg = res.json()['books'][0].get('average_rating')
        revdata=db.execute("select tbuser.username, tb_review.review_num, tb_review.review_message from book inner join tb_review ON tb_review.id = book.id inner join tbuser on tbuser.user_id = tb_review.user_id WHERE book.id =:id", {"id":bookid}).fetchall()
        if revdata is None:
            return render_template('review.html', rmsg="No Reviews found on this book", book=data,avgRating=ratingAvg, numRating=ratingNum)
        else:
            return render_template('review.html', reviews=revdata, book=data, avgRating=ratingAvg, numRating=ratingNum)

    else:
        return render_template('review.html', msg="you have to login first", book=data)
@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return render_template("singup.html")
    
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/submit-review/<bookid>", methods=['POST'])
def submit_rev(bookid):
    rn = request.form.get('review_num')
    rm =request.form.get('review_msg')
    uid = session['uid']
    if not db.execute("SELECT * FROM tb_review where user_id=:userid and id=:bid",{"userid":uid, "bid":bookid}).fetchone():
        if db.execute("INSERT INTO tb_review(id,review_message,user_id,review_num) VALUES(:bid,:rm,:uid,:rn)",{"bid":bookid, "rm":rm, "uid":uid, "rn": rn}):
            db.commit()
            return ("Thank your for reviewing this book")
        else:
            return ("Failed to review this book due to some....")
    else:
        return ("SORRY! you are allready reviewed this book")
    return render_template('index.html')

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    bdata = db.execute("SELECT * FROM book WHERE isbn = :bisbn", {"bisbn": isbn}).fetchone()
    if bdata is None:
        return "No Such A Book in the Database", 404
    bookid = db.execute("SELECT id from book where isbn =:isbn",{"isbn":isbn}).fetchone()


    numOfRatings = db.execute("SELECT COUNT (*) FROM tb_review WHERE id = :book_id", {"book_id": bookid.id}).fetchone()
    averageRating = db.execute("SELECT AVG (review_num) FROM tb_review WHERE id = :book_id", {"book_id": bookid.id}).fetchone()

    app.logger.debug(f'numOfRatings type is {type(numOfRatings)}, value is {numOfRatings}')
    app.logger.debug(f'averageRating type is {type(averageRating)}, value is {averageRating}')

    response = {}
    response['title'] = bdata.title 
    response['author'] = bdata.author
    response['year'] = bdata.year
    response['isbn'] = bdata.isbn
    response['review_count'] = str(numOfRatings[0])
    response['average_score'] = '% 1.1f' % averageRating[0]

    json_response = json.dumps(response)

    return json_response, 200

if __name__ == "__main__":
    app.run(debug=True)
