from flask import Flask, render_template ,request, session, redirect, url_for
import pymysql
import flask
from werkzeug.utils import secure_filename
from flask import send_from_directory
import itertools
import random
import math
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
#--------------------------------------------------------------
#アップロード先の設定と、ファイル名の確認関数
''' app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS '''
#--------------------------------------------------------------
#ページ系削除使用リスト
pop_list_page = ["page_number","page_number_web","page_number_AI","page_number_VR","page_number_XR","page_number_Unity","page_number_iOS","page_number_Android"]
#--------------------------------------------------------------
def getConnection():
    return pymysql.connect(
        host='localhost',
        db='db名',
        user='ユーザ名',
        password='パスワード',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
#--------------------------------------------------------------
#スタート
@app.route('/')
def start():
    return render_template("start.html")

#--------------------------------------------------------------
#indexのやつ
@app.route('/index', methods=["POST","GET"])
def index():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number":
            session.pop(popping,None)



    if "belong" not in session:
        session["belong"] = request.form["belong"]
        belong = session["belong"]
        belong = int(belong)
    else:
        belong = session["belong"]
        belong = int(belong)

    if "name" not in session:
        if belong == 0:
            session["name"] = request.form["name"]
            session["sc_number"] = request.form["sc_number"]
            name = session["name"]
            sc_number = session["sc_number"]
        else:
            session["name"] = "訪問者"
            session["sc_number"] = 0
            name = session["name"]
            sc_number = session["sc_number"]
    else:
        sc_name = session["name"]
        sc_number = session["sc_number"]
    
    if "page_number" not in session:
        session["page_number"] = 1
        page_number = int(session["page_number"])
    else:
        session["page_number"] = request.form["page_number"]
        page_number = int(session["page_number"])
    
    #セッションから引っ張ってきたやつ全部strになってる(なんで???)
    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #SQLからログインデータ取得
    connection = getConnection()

    #学籍番号and名前
    sql = "SELECT * FROM test_login where sc_number =" + str(sc_number)
    cursor = connection.cursor()
    cursor.execute(sql)
    sc_sql = cursor.fetchall()

    #掲載物用sql
    sql_public = "SELECT * FROM pre_publication"
    cursor_public = connection.cursor()
    cursor_public.execute(sql_public)
    public_from_sql = cursor_public.fetchall()
    if len(sc_sql) <= 0:
        y = 0
    else:
        y = 1
        #名前、学籍番号
        sc_number_sql = [d.get('sc_number') for d in sc_sql]
        sc_name_sql = [d.get('name') for d in sc_sql]
        sc_number_send = sc_number_sql[0]
        sc_name_send = sc_name_sql[0]

        #掲載用
    public_id = [d.get("publication_id") for d in public_from_sql]
    public_name = [d.get("publication_name") for d in public_from_sql]
    public_image = [d.get("publication_image") for d in public_from_sql]

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    

    #掲載用画像をパスに変換用
    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    #ページ番号数
    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)
    
    #次は画像の掲載とPDFのアップロードを作成
    #その後マイページ作成
    cursor.close()
    connection.close()

    if y == 1:
        #訪問者はid0
        if sc_number_send == 0:
            return render_template("index.html",
            #name:名前、sc_number:学籍番号
            name = "訪問者", sc_number=sc_number_send,
            #public_id:掲載用id、public_name:掲載用名前、public_image:掲載用PASS
            public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
            #ページ番号、これを利用して表示する研究内容の頭数字を決定
            page_number_from_py = page_number, start_pub_number=start_pub_number,end_pub_number=end_pub_number,
            #画像のパス
            public_image_pass=image_list,
            #ページ番号表示用
            page_make_list=page_make_list,page_make_number=page_make_number,
            )
        #内部用
        else:
            #name:名前、sc_number:学籍番号、public_id:掲載用id、public_name:掲載用名前、public_image:掲載用PASS
            return render_template("index.html",
            #name:名前、sc_number:学籍番号
            name = sc_name_send, sc_number=sc_number_send,
            #public_id:掲載用id、public_name:掲載用名前、public_image:掲載用PASS
            public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
            #ページ番号、これを利用して表示する研究内容の頭数字を決定
            page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
            #画像のパス
            public_image_pass=image_list,
            #ページ番号表示用
            page_make_list=page_make_list,page_make_number=page_make_number,
            )
    else:
        return "Name or Password is False(`A´)"
    
#--------------------------------------------------------------
#ホームページのやつ
@app.route('/your_home')
def homepage():
    #名前と学籍番号取っておく
    name = session["name"]
    sc_number = session["sc_number"]

    #ホームに出す自分の投稿物を表示
    connection = getConnection()
    sql_home = "SELECT * FROM pre_publication where sc_number =" + str(sc_number)
    cursor = connection.cursor()
    cursor.execute(sql_home)
    home_sql = cursor.fetchall()
    public_id = [d.get("publication_id") for d in home_sql]
    public_name = [d.get("publication_name") for d in home_sql]
    public_image = [d.get("publication_image") for d in home_sql]

    how_many_public = len(public_id)

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)

    return render_template("your_home.html",
    name=name,sc_number=sc_number,
    public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
    public_image_pass=image_list,
    how_many_public=how_many_public,
    )

#--------------------------------------------------------------
#検索用Web、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_Web",methods=["POST","GET"])
def search_web():
    for popping in pop_list_page:
        if not popping == "page_number_web":
            session.pop(popping,None)


    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_web" not in session:
        session["page_number_web"] = 1
        page_number = session["page_number_web"]
    else:
        session["page_number_web"] = request.form["page_number_web"]
        page_number = session["page_number_web"]
    
    connection = getConnection()
    sql_web = "SELECT * FROM pre_publication where tags = 'Web'"
    cursor_public_web = connection.cursor()
    cursor_public_web.execute(sql_web)
    web_from_sql = cursor_public_web.fetchall()

    public_id = [d.get("publication_id") for d in web_from_sql]
    public_name = [d.get("publication_name") for d in web_from_sql]
    public_image = [d.get("publication_image") for d in web_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_web' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_web.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用AI、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_AI",methods=["POST","GET"])
def search_AI():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_AI":
            session.pop(popping,None)


    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_AI" not in session:
        session["page_number_AI"] = 1
        page_number = session["page_number_AI"]
    else:
        session["page_number_AI"] = request.form["page_number_AI"]
        page_number = session["page_number_AI"]
    
    connection = getConnection()
    sql_AI = "SELECT * FROM pre_publication where tags = 'AI'"
    cursor_public_AI = connection.cursor()
    cursor_public_AI.execute(sql_AI)
    AI_from_sql = cursor_public_AI.fetchall()

    public_id = [d.get("publication_id") for d in AI_from_sql]
    public_name = [d.get("publication_name") for d in AI_from_sql]
    public_image = [d.get("publication_image") for d in AI_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_AI' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_AI.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用VR、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_VR",methods=["POST","GET"])
def search_VR():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_VR":
            session.pop(popping,None)

    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_VR" not in session:
        session["page_number_VR"] = 1
        page_number = session["page_number_VR"]
    else:
        session["page_number_VR"] = request.form["page_number_VR"]
        page_number = session["page_number_VR"]
    
    connection = getConnection()
    sql_VR = "SELECT * FROM pre_publication where tags = 'VR'"
    cursor_public_VR = connection.cursor()
    cursor_public_VR.execute(sql_VR)
    VR_from_sql = cursor_public_VR.fetchall()

    public_id = [d.get("publication_id") for d in VR_from_sql]
    public_name = [d.get("publication_name") for d in VR_from_sql]
    public_image = [d.get("publication_image") for d in VR_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_VR' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_VR.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用XR、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_XR",methods=["POST","GET"])
def search_XR():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_XR":
            session.pop(popping,None)

    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_XR" not in session:
        session["page_number_XR"] = 1
        page_number = session["page_number_XR"]
    else:
        session["page_number_XR"] = request.form["page_number_XR"]
        page_number = session["page_number_XR"]
    
    connection = getConnection()
    sql_XR = "SELECT * FROM pre_publication where tags = 'XR'"
    cursor_public_XR = connection.cursor()
    cursor_public_XR.execute(sql_XR)
    XR_from_sql = cursor_public_XR.fetchall()

    public_id = [d.get("publication_id") for d in XR_from_sql]
    public_name = [d.get("publication_name") for d in XR_from_sql]
    public_image = [d.get("publication_image") for d in XR_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_XR' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_XR.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用Unity、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_Unity",methods=["POST","GET"])
def search_Unity():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_Unity":
            session.pop(popping,None)

    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_Unity" not in session:
        session["page_number_Unity"] = 1
        page_number = session["page_number_Unity"]
    else:
        session["page_number_Unity"] = request.form["page_number_Unity"]
        page_number = session["page_number_Unity"]
    
    connection = getConnection()
    sql_Unity = "SELECT * FROM pre_publication where tags = 'Unity'"
    cursor_public_Unity = connection.cursor()
    cursor_public_Unity.execute(sql_Unity)
    Unity_from_sql = cursor_public_Unity.fetchall()

    public_id = [d.get("publication_id") for d in Unity_from_sql]
    public_name = [d.get("publication_name") for d in Unity_from_sql]
    public_image = [d.get("publication_image") for d in Unity_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_Unity' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_Unity.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用iOS、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_iOS",methods=["POST","GET"])
def search_iOS():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_iOS":
            session.pop(popping,None)

    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_iOS" not in session:
        session["page_number_iOS"] = 1
        page_number = session["page_number_iOS"]
    else:
        session["page_number_iOS"] = request.form["page_number_iOS"]
        page_number = session["page_number_iOS"]
    
    connection = getConnection()
    sql_iOS = "SELECT * FROM pre_publication where tags = 'iOS'"
    cursor_public_iOS = connection.cursor()
    cursor_public_iOS.execute(sql_iOS)
    iOS_from_sql = cursor_public_iOS.fetchall()

    public_id = [d.get("publication_id") for d in iOS_from_sql]
    public_name = [d.get("publication_name") for d in iOS_from_sql]
    public_image = [d.get("publication_image") for d in iOS_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_iOS' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_iOS.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )

#--------------------------------------------------------------
#検索用Android、今はタグSQLまで出来てるから次はここに送るボタンをindexに作成し、indexぽく表示
@app.route("/search_Android",methods=["POST","GET"])
def search_Android():
    #ページ系セッション削除
    for popping in pop_list_page:
        if not popping == "page_number_Android":
            session.pop(popping,None)

    name = session["name"]
    sc_number = session["sc_number"]

    if "page_number_Android" not in session:
        session["page_number_Android"] = 1
        page_number = session["page_number_Android"]
    else:
        session["page_number_Android"] = request.form["page_number_Android"]
        page_number = session["page_number_Android"]
    
    connection = getConnection()
    sql_Android = "SELECT * FROM test_publication where tags = 'Android'"
    cursor_public_Android = connection.cursor()
    cursor_public_Android.execute(sql_Android)
    Android_from_sql = cursor_public_Android.fetchall()

    public_id = [d.get("publication_id") for d in Android_from_sql]
    public_name = [d.get("publication_name") for d in Android_from_sql]
    public_image = [d.get("publication_image") for d in Android_from_sql]

    image_list = []
    for im in public_image:
        image_pass = "<img src=static/" + im + " >"
        image_list.append(image_pass)

    page_make_list = []
    num_page = len(public_id) / 10
    if isinstance(num_page,float):
        num_page = math.floor(num_page)
        num_page += 1
    else:
        num_page += 1
    for i in range(1,num_page):
        page_make_list.append("<button type='submit' style='font-size:20px; margin-top:5px; border-style: none;' name='page_number_Android' value='" + str(i) + "'>" + str(i) + "</button>")
    page_make_number = len(page_make_list)

    nanikore = int(page_number)
    start_pub_number = nanikore * 10-10
    end_pub_number = nanikore * 10

    #掲載リンク用
    public_name_pass = []
    name_value = []
    pn_count = 0
    for pn in public_name:
        name_pass = '<a href="javascript:pdf_id[' + str(pn_count) + '].submit()" style="color:black; text-decoration:none; text-decoration: none; font-weight:bold; font-size:25px;">' + str(pn) + '</a>'
        public_name_pass.append(name_pass)
        pn_count += 1

    for name_id in public_id:
        id_pass = '<input type="hidden" value="' + str(name_id) + '" name="pdf_id">'
        name_value.append(id_pass)

    #フォーム作成用
    form_public = []
    for fp in range(1,len(public_id)+1):
        forms = "<form action='/show_search' method='post'  name='pdf_id" + str(fp) + "'>"
        form_public.append(forms)
    
    return render_template(
        "search_Android.html",
        name=name,sc_number=sc_number,
        public_id = name_value, public_name = public_name_pass, public_iamge = public_image,
        page_number_from_py = page_number,start_pub_number=start_pub_number,end_pub_number=end_pub_number,
        public_image_pass=image_list,
        page_make_list=page_make_list,page_make_number=page_make_number
    )
    #タグ検索まで

#--------------------------------------------------------------
#研究の詳細表示
@app.route("/show_search",methods=["POST","GET"])
def show_search():
    for popping in pop_list_page:
        session.pop(popping,None)

    pdf_id = request.form["pdf_id"]

    connection = getConnection()
    sql_public = "SELECT * FROM test_publication WHERE publication_id=" + str(pdf_id)
    cursor_public = connection.cursor()
    cursor_public.execute(sql_public)
    public_from_sql = cursor_public.fetchall()
    public_id = [d.get("publication_id") for d in public_from_sql]
    public_name = [d.get("publication_name") for d in public_from_sql]
    public_image = [d.get("publication_image") for d in public_from_sql]
    pdf_pass = [d.get("pdf_pass") for d in public_from_sql]

    ppp = public_name[0]
    pdf_pass_send = '<embed src="' + str(pdf_pass[0]) + '" width="800px" height="700px" />'

    return render_template("show_search.html",ppp=ppp,pdf_pass_send=pdf_pass_send)

#--------------------------------------------------------------
@app.route("/send_public",methods=["POST","GET"])
def send_public():
    return render_template("send_pub.html")


#--------------------------------------------------------------
#pdf完了
@app.route("/pub_comp",methods=["POST","GET"])
def pub_comp():
    for popping in pop_list_page:
        session.pop(popping,None)


    #アップロード者の学籍番号
    sc_number = session["sc_number"]

    #アップロードのID取得
    connection = getConnection()
    sql_public = "SELECT * FROM test_publication ORDER BY publication_id DESC LIMIT 1"
    cursor_public = connection.cursor()
    cursor_public.execute(sql_public)
    public_from_sql = cursor_public.fetchall()
    public_id = [d.get("publication_id") for d in public_from_sql]
    upload_id = public_id[0] + 1

    #アップロードするpublication_name取得
    upload_name = request.form["upload_name"]

    #アップロードするpublication_image取得
    if request.method == 'POST':
        upload_image = request.files["file_image"]
        #任意の階層をフルパスで指定(macの場合。任意のユーザー名は変更してください。)
        upload_image.save('./static/' + str(upload_name) + ".png")
        upload_image_pass = str(upload_name) + ".png"
    
    #アップロードするpdf取得
    if request.method == 'POST':
        upload_pdf = request.files["file_pdf"]
        upload_pdf.save('./static/' + str(upload_name) + ".pdf")
        upload_pdf_pass = './static/' + str(upload_name) + ".pdf"

    #アップロードするタグ
    upload_tags = request.form["upload_tags"]
    
    cursor_upload = connection.cursor()
    upload_sql = "INSERT INTO test_publication (publication_id,publication_name,publication_image,sc_number,tags,pdf_pass) VALUES (" + str(upload_id) + ",'" + str(upload_name) + "','" + str(upload_image_pass) + "'," + str(sc_number) + ",'" + str(upload_tags) + "','" + str(upload_pdf_pass) + "')"
    cursor_upload.execute(upload_sql)
    connection.commit()

    sql = "SELECT * FROM test_publication"
    cursor_upload.execute(sql)
    players = cursor_upload.fetchall()


    return render_template("pub_comp.html",players=players)
