from __future__ import print_function
#from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from flask.ext.mobility import Mobility
from flask.ext.mobility.decorators import mobile_template
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import desc

from flask import jsonify
import sys
import os
from helpers import apology, login_required
import json
import redis

# Configure application
app = Flask(__name__)
Mobility(app)

@app.before_request
def make_session_permanent():
    session.permanent = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = 'redis' #'memcached' #'redis'# #"filesystem"
#app.config["SESSION_REDIS"] = 'redis://h:pd834160182df6dadd4e7fa1f9ff67e89f1329d0beb0e81d78f66950bac972ad9@ec2-18-204-181-140.compute-1.amazonaws.com:20079'
app.config["SESSION_REDIS"] = redis.from_url('redis://h:pd834160182df6dadd4e7fa1f9ff67e89f1329d0beb0e81d78f66950bac972ad9@ec2-18-204-181-140.compute-1.amazonaws.com:20079')
# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")
#db = SQL("sqlite:///pathgame.db")
#use SQL_alchemy to connect to the heroku database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
Session(app)
#sess = Session()

#sess.init_app(app)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passwd = db.Column(db.String(256), nullable=False)
    sex = db.Column(db.Integer, nullable=True)
    age = db.Column(db.Integer, nullable=True)

    games = db.relationship("Game", backref="user")
    hiscore = db.relationship("Hiscore", backref="user")
    level = db.Column(db.Integer)
    gamesplayed = db.Column(db.Integer)

    def __init__(self, name, passwd):
        self.username = name
        self.passwd = passwd
        self.level = 1
        self.gamesplayed = 0

class Game(db.Model):
    db.__tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    time = db.Column(db.Float, nullable=False)
    pathlength = db.Column(db.Float, nullable=False)
    destinationpoints = db.Column(db.String(4096), nullable=False)
    pathpoints = db.Column(db.String(4096), nullable=False)
    numdestpoints = db.Column(db.Integer)
    level = db.Column(db.Integer)
    score = db.Column(db.Integer)   # 3000 - pathlength/numdestpoints + (10 - time/numdestpoints)*numdestpoints

    game = db.relationship('Hiscore', backref="game")

    def __init__(self, userid, time, pathlength, destinationpoints, pathpoints, numdestpoints, level, score):
        self.userid = userid
        self.time = time
        self.pathlength = pathlength
        self.destinationpoints = destinationpoints
        self.pathpoints = pathpoints
        self.numdestpoints = numdestpoints
        self.level = level
        self.score = score

class Hiscore(db.Model):
    db.__tablename__ = 'hiscore'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    besttime = db.Column(db.Float, nullable=False)
    shortestpathlength = db.Column(db.Float, nullable=False)
    gameid = db.Column(db.Integer, db.ForeignKey("game.id"))
    score = db.Column(db.Integer)   # 3000 - shortestpathlength/numdestpoints + (10 - besttime/numdestpoints)*numdestpoints
    #user = db.relationship('User',
    #    backref=db.backref('hiscore', lazy=True))

    def __init__(self, userid, time, pathlength, gameid, score):
        self.userid = userid
        self.besttime = time
        self.shortestpathlength = pathlength
        self.gameid = gameid
        self.score = score

class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)

    def __init__(self, email):
        self.email = email

@app.route("/")
@login_required
def index():
    return render_template("index.html", level = session['level'])

@app.route("/login", methods=["GET", "POST"])
@mobile_template('{mobile/}login.html')
def login(template):
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if request.MOBILE:
            if not request.form.get("email"):
                return apology("must provide email", 403)

            exist_email = Email.query.filter(Email.email == request.form.get("email")).first()
            if exist_email != None:
                return apology("email already exists", 403)

            new_email = Email(request.form.get("email"))

            db.session.add(new_user)
            db.session.commit()

        else:
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
            session['user_id'] = curr_user.id #rows[0]["userid"]
            session['level'] = curr_user.level
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
        sex = request.form.get("sex")
        age = request.form.get("age")
        new_user = User(name, generate_password_hash(request.form.get("password")))
        new_user.sex = sex;
        new_user.age = age;

        if User.query.filter(User.username == name).first() != None:
             return apology("username already exists", 400)

        db.session.add(new_user)
        db.session.commit()

        #get the id
        new_user = User.query.filter(User.username == name).first()

        #result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
        #                    username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        #if not result:
        #    return apology("izaberi drugo ime")
        # Remember which user has logged in
        session['user_id'] = new_user.id
        session['level'] = 1    #everybody starts at level 1
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/postmethod', methods = ['POST'])
@login_required
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
                print('num dest points was: ' + str(jsondata['numdestpoints']) + '\n')

                for item in jsondata:
                    print(item)

                print(jsondata['pathpoints'])

                score = 3000 - jsondata['pathlength']/jsondata['numdestpoints'] + (10 - jsondata['time']/jsondata['numdestpoints'])*jsondata['numdestpoints'] # 3000 - pathlength/numdestpoints + (10 - time/numdestpoints)*numdestpoints

                #store the game
                result = Game(session['user_id'], jsondata['time'], jsondata['pathlength'],
                    str(jsondata['pointsdestination']), str(jsondata['pathpoints']), jsondata['numdestpoints'], session['level'], score)
                #result = db.execute("INSERT INTO games (userid, time, pathlength, destinationpoints, pathpoints) VALUES(:userid, :time, :pathlength, :destinationpoints, :pathpoints)",
                #    userid=session["user_id"], time=jsondata['time'], pathlength = jsondata['pathlength'],
                #    destinationpoints = str(jsondata['pointsdestination']), pathpoints = str(jsondata['pathpoints']))

                db.session.add(result)

                db.session.flush() #to get the game.id assigned

                #increase the user level
                result.user.level = result.user.level + 1;

                #update hiscores
                rows = Hiscore.query.filter(Hiscore.userid == session['user_id']).all()
                #rows = db.execute("SELECT * FROM hiscores WHERE userid = :userid",
                #          userid=session['user_id'])

                # Ensure username exists and password is correct
                if len(rows) != 1:
                    new_hiscore = Hiscore(session['user_id'], str(jsondata['time']), str(jsondata['pathlength']), result.id, score)
                    #result = db.execute("INSERT INTO hiscores (userid, besttime, shortestpathlength) VALUES(:userid, :time, :pathlength)",
                    #userid=session['user_id'], time=jsondata['time'], pathlength = jsondata['pathlength'])
                    db.session.add(new_hiscore)
                else:
                    if rows[0].score < score:
                    #if rows[0].shortestpathlength > jsondata['pathlength'] and rows[0].besttime > jsondata['time']:
                        rows[0].besttime = jsondata['time']
                        rows[0].shortestpathlength = jsondata['pathlength']
                        rows[0].userid = session['user_id']
                        rows[0].gameid = result.id
                        rows[0].score = score
                    #if rows[0]['shortestpathlength'] > jsondata['pathlength'] and rows[0]['besttime'] > jsondata['time']:
                        #result = db.execute("UPDATE hiscores (besttime, shortestpathlength) VALUES(:time, :pathlength) WHERE userid = :userid",
                        #    time=jsondata['time'], pathlength = jsondata['pathlength'], userid=session['user_id'])
                db.session.commit()

                session['level'] = result.user.level #update the session level

                print('user level is: ' + str(session['level']) + '\n')


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

@app.route("/scores", methods = ['GET'])
def scores():
    #rows = db.execute("SELECT username, shortestpathlength, besttime FROM hiscores INNER JOIN users ON hiscores.userid = users.userid LIMIT 10;")
    #rows = Hiscore.query.order_by(Hiscore.shortestpathlength,Hiscore.besttime).limit(10)
    rows = Hiscore.query.order_by(desc(Hiscore.score)).limit(10)
    print(rows)
    return render_template("scores.html", scores = rows)

@app.route("/back")
@login_required
def back():
    return render_template("index.html", level = session['level'])

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
