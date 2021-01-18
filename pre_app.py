from flask import Flask, render_template
import pymysql
app = Flask(__name__)

def getConnection():
    return pymysql.connect(
        host='localhost',
        db='future_app',
        user='pokurin',
        password='0831',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def select_sql():
    connection = getConnection()
    message = "Hello world"

    sql = "SELECT * FROM my_spot4"
    cursor = connection.cursor()
    cursor.execute(sql)
    players = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('index.html', message = message, players = players)