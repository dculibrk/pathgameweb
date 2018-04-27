from __future__ import print_function
#from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from flask import jsonify
import sys
import os
from helpers import apology, login_required
import json

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")
#db = SQL("sqlite:///pathgame.db")
#use SQL_alchemy to connect to the heroku database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passwd = db.Column(db.String(256), nullable=False)
    sex = db.Column(db.Integer, nullable=True)
    age = db.Column(db.Integer, nullable=True)

    games = db.relationship("Game", backref="user")
    hiscores = db.relationship("Hiscore", backref="user")

    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd

class Game(db.Model):
    db.__tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    time = db.Column(db.Float, nullable=False)
    pathlength = db.Column(db.Float, nullable=False)
    destinationpoints = db.Column(db.String(4096), nullable=False)
    pathpoints = db.Column(db.String(4096), nullable=False)

    #user = db.relationship('User',
    #    backref=db.backref('games', lazy=True))

    def __init__(self, userid, time, pathlength, destinationpoints, pathpoints):
        self.userid = userid
        self.besttime = time
        self.shortestpathlength = pathlength
        self.destinationpoints = destinationpoints
        self.pathpoints = pathpoints

class Hiscore(db.Model):
    db.__tablename__ = 'hiscore'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    besttime = db.Column(db.Float, nullable=False)
    shortestpathlength = db.Column(db.Float, nullable=False)

    #user = db.relationship('User',
    #    backref=db.backref('hiscore', lazy=True))

    def __init__(self, userid, time, pathlength):
        self.userid = userid
        self.besttime = time
        self.shortestpathlength = pathlength

@app.route("/")
@login_required
def index():



    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        #rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                  username=request.form.get("username"))

        # Ensure username exists and password is correct
        curr_user = User.query.filter(User.username == request.form.get("username")).first()
        if curr_user == None or not check_password_hash(curr_user.passwd, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        #if len(rows) != 1 or not check_password_hash(rows[0]["passwd"], request.form.get("password")):
        #    return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = curr_user.id #rows[0]["userid"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation of password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation doesn't match", 400)

        name = request.form.get("username")
        new_user = User(name, generate_password_hash(request.form.get("password")))

        if User.query.filter(User.username == name).first() != None:
             return apology("username already exists", 400)

        db.session.add(new_user)
        db.session.commit()

        #result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
        #                    username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        if not result:
            return apology("izaberi drugo ime")
        # Remember which user has logged in
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    if request.method == "POST":
        jsdata = request.form.get('javascript_data') #request.form['javascript_data']

        if jsdata:
            print('got some jsdata!\n')

            jsondata = json.loads(jsdata)

            if jsondata:
                print('got some json data!\n')
                print('time was: ' + str(jsondata['time']) + '\n')
                print('length was: ' + str(jsondata['pathlength']) + '\n')

                for item in jsondata:
                    print(item)

                print(jsondata['pathpoints'])

                #store the game
                result = Game(session["user_id"], jsondata['time'], jsondata['pathlength'],
                    str(jsondata['pointsdestination']), str(jsondata['pathpoints']))
                #result = db.execute("INSERT INTO games (userid, time, pathlength, destinationpoints, pathpoints) VALUES(:userid, :time, :pathlength, :destinationpoints, :pathpoints)",
                #    userid=session["user_id"], time=jsondata['time'], pathlength = jsondata['pathlength'],
                #    destinationpoints = str(jsondata['pointsdestination']), pathpoints = str(jsondata['pathpoints']))
                db.session.add(result)

                #update hiscores
                rows = Hiscore.query.filter(Hiscore.userid == session['user_id']).all()
                #rows = db.execute("SELECT * FROM hiscores WHERE userid = :userid",
                #          userid=session['user_id'])

                # Ensure username exists and password is correct
                if len(rows) != 1:
                    new_hiscore = Hiscore(session['user_id'], jsondata['time'], jsondata['pathlength'])
                    #result = db.execute("INSERT INTO hiscores (userid, besttime, shortestpathlength) VALUES(:userid, :time, :pathlength)",
                    #userid=session['user_id'], time=jsondata['time'], pathlength = jsondata['pathlength'])
                    db.session.add(result)
                else:
                    if rows[0].shortestpathlength > jsondata['pathlength'] and rows[0].besttime > jsondata['time']:
                        rows[0].besttime = jsondata['time']
                        rows[0].shortestpathlength = jsondata['pathlength']
                        roes[0].userid = session['user_id']
                    #if rows[0]['shortestpathlength'] > jsondata['pathlength'] and rows[0]['besttime'] > jsondata['time']:
                        #result = db.execute("UPDATE hiscores (besttime, shortestpathlength) VALUES(:time, :pathlength) WHERE userid = :userid",
                        #    time=jsondata['time'], pathlength = jsondata['pathlength'], userid=session['user_id'])
                db.session.commit()
    return 'nja' # json.loads(jsdata)[0]

@app.route('/receiver', methods = ['POST'])
def worker():
    # read json + reply
    print('query arrived in /receiver!\n')
    jsondata = request.get_json(force=True); #jsonify(request.json);
    result = ''
    if jsondata:
        print('got some data!\n')

        for item in jsondata:
            # loop over every row
            result += str(item['pointsdestination']) + '\n'
    return result

@app.route("/scores", methods = ['GET','POST'])
def scores():
    #rows = db.execute("SELECT username, shortestpathlength, besttime FROM hiscores INNER JOIN users ON hiscores.userid = users.userid LIMIT 10;")
    rows = Hiscore.query .top(10)
    print(rows)
    return render_template("scores.html", scores = rows)




@app.route("/back")
def back():


    return render_template("index.html")










def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
