from flask import Flask, render_template ,request, session
import pymysql
import itertools

app = Flask(__name__)
app.secret_key = "1850_0831"

#スタート
@app.route('/')
def start():
    return render_template("start.html")

@app.route('/index', methods=["POST"])
def home():
    if "name" not in session:

        session["name"] = request.form["name"]
        session["sc_number"] = request.form["sc_number"]
        name = session["name"]
        number = session["sc_number"]
    else:
        name = session["name"]
        number = session["sc_number"]
    return render_template("unchi.html",name=name,sc_number=number)
