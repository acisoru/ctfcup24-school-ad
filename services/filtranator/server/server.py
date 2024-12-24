#!/usr/bin/python3
from flask import (
    Flask,
    redirect,
    url_for,
    request,
    make_response,
    render_template_string,
    render_template,
    abort,
)
from app.db import LocalDb
import os
import string
import random
import subprocess
import sys

appx = Flask(__name__)


def generate_cock():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(32))


def db_conn():
    mydb = LocalDb()
    conn_string = "host='db' dbname = 'Users' user='postgres' password = 'password'"
    mydb.connect(conn_string)
    return mydb


@appx.route("/")
def redir():
    return redirect(url_for("login"))


@appx.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form["username"]
        password = request.form["password"]

        if name != "" and password != "":
            # mydb = db_conn()
            # try:
            result = mydb.execute(
                "SELECT * FROM Users WHERE username='" + name + "';")
            print(result, file=sys.stderr)
            if result != []:
                return "<p1>User alredy exist</p1>"
            print(name, file=sys.stderr)
            mydb.execute(
                "INSERT INTO Users (username,password) VALUES ('"
                + name
                + "','"
                + password
                + "');"
            )
            if not os.path.isdir("./images/" + name):
                os.mkdir("./images/" + name)
            return "<p1>Sucessfully registered<p1>"
            # except Exception as e:
            #    return "Exception"
        return "<p1>Vvedi normalniye credi ti che</p1>"


@appx.route("/login", methods=["GET", "POST"])
def login():
    global logged_users
    if request.method == "GET":
        return render_template("login.html")
    else:
        print("Login entered...")
        name = request.form["username"]
        password = request.form["password"]
        if name != "" and password != "":
            if name in logged_users.values():
                return "<p1>Already logged in</p1>"
            # mydb = db_conn()
            # try:
            result = mydb.execute(
                "SELECT * FROM Users WHERE username='"
                + name
                + "' AND password='"
                + password
                + "';"
            )
            if result == []:
                abort(404)
            cock = generate_cock()
            if len(logged_users) > 10000:
                logged_users = {}
            logged_users[cock] = name
            resp = make_response(
                render_template_string("<p1>Sucessfully logged in<p1>")
            )
            resp.set_cookie("token", cock)
            return resp
            # except Exception as e:
            #    return "Exeception"
        return render_template_string("<p1>Vvedi normalniye credi ti che<p1>")


@appx.route("/logout", methods=["GET"])
def logout():
    cock = request.cookies.get("token")
    if cock is None:
        abort(401)
    elif logged_users.get(cock) is None:
        abort(401)
    del logged_users[cock]
    return "<p1>Sucessfully logout</p1>"


@appx.route("/images", methods=["GET"])
def get_images():
    cock = request.cookies.get("token")
    if cock is None:
        abort(401)
    elif logged_users.get(cock) is None:
        abort(401)
    usr = logged_users.get(cock)
    path = "./images/" + usr
    onlyfiles = [f for f in os.listdir(
        path) if os.path.isfile(os.path.join(path, f))]
    if len(onlyfiles) < 1:
        return "<p1>No images</p1>"
    img = onlyfiles[0]
    image_binary = open("./images/" + usr + "/" + img, "rb").read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/png")
    response.headers.set("Content-Disposition",
                         "attachment", filename="%s.png" % img)
    return response


@appx.route("/apply_filter", methods=["GET", "POST"])
def filtrate():
    cock = request.cookies.get("token")
    if cock is None:
        abort(401)
    elif logged_users.get(cock) is None:
        abort(401)
    if request.method == "GET":
        return render_template("apply_filter.html")
    else:
        filter_name = request.form["filter"]
        filename = request.form["filename"]
        imagefile = request.files.get("image", "")
        print(imagefile,file=sys.stderr)
        if imagefile is None:
            return "<p1>Undefined</p1>"
        usr = logged_users.get(cock)
        if filename == "":
            return "<p1>Undefined filename</p1>"
        imagefile.save("./images/" + usr + "/" + filename)
        path = "./images/" + usr + "/" + filename
        if filter_name == "black":
            subprocess.Popen(["./filterer/filterer", path, "black"])
            return "<p1>Image blacked</p1>"
        elif filter_name == "none":
            return "<p1>Image saved</p1>"
        return "<p1>Undefined</p1>"


global logged_users
global mydb

if __name__ == "__main__":
    mydb = db_conn()
    logged_users = {}
    appx.run(host="0.0.0.0", port=6969)
