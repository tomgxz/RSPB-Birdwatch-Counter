"""
Dependencies:
    flask
    flask-login
    flask-sqlalchemy
    sqlite3
"""
from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user


db=SQLAlchemy(session_options={"autoflush": False})

class RSBPBirdwatchSite():

    global db

    def __init__(self,host,port):

        import os,sqlite3,datetime
        self.os=os
        self.sqlite3=sqlite3
        self.datetime=datetime

        self.db=db

        self.initFlask()

        self.db.init_app(self.app)

        self.loginManager=LoginManager()
        self.loginManager.login_view="auth_login"
        self.loginManager.init_app(self.app)

        from models import User
        self.User = User

        @self.loginManager.user_loader
        def loadUser(user_id):
            return self.User.query.get(user_id)

        self.app.run(host=host,port=port)

    def initFlask(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"]="secret-key-goes-here"
        self.app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///db.sqlite"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.initPages()

    def initPages(self):
        self.initPages_main()
        self.initPages_auth()

        @self.app.route("/<name>/<site>/")
        @self.app.route("/<name>/<site>/home/")
        @login_required
        def site_edit_home(name=None,site=None):
            flash(1)
            flash(name)
            flash(site)
            if current_user.user_id!=name: return "External view of site"
            return render_template("site-edit-home.html")

        @self.app.route("/<name>/<site>/edit/")
        def  site_edit_app(name=None,site=None):
            return "bsknbosknfbolektnabe now edit things"

    def initPages_main(self):
        @self.app.route("/")
        def main_index(): return redirect(url_for("auth_login"))

        @self.app.route("/home/")
        @login_required
        def main_home():
            flash(self.getBirdDictForFlash())
            flash("")
            return render_template("home.html")

        @self.app.route("/home/",methods=["post"])
        @login_required
        def main_home_post():
            birdname = request.form.get("bird_form_name").lower()
            birdamt = request.form.get("bird_form_amount")

            if birdname=="" or birdamt=="":
                flash(self.getBirdDictForFlash())
                flash("Fill out all fields please")
                return redirect(url_for("main_home"))

            if birdname not in ["robin","blackbird","pigeon","magpie","blue tit","thrush","wren","starling"]:
                flash(self.getBirdDictForFlash())
                flash("Unrecognised bird")
                return redirect(url_for("main_home"))

            if not birdamt.isdigit():
                flash(self.getBirdDictForFlash())
                flash("That isn't a valid number")
                return redirect(url_for("main_home"))

            birdamt=int(birdamt)

            user = db.session.query(self.User).filter_by(user_id=current_user.user_id).first()

            if birdname == "robin":
                user.robin+=birdamt
            elif birdname == "blackbird":
                user.blackbird+=birdamt
            elif birdname == "pigeon":
                user.pigeon+=birdamt
            elif birdname == "magpie":
                user.magpie+=birdamt
            elif birdname == "blue tit":
                user.blue_tit+=birdamt
            elif birdname == "thrush":
                user.thrush+=birdamt
            elif birdname == "wren":
                user.wren+=birdamt
            elif birdname == "starling":
                user.starling+=birdamt

            self.db.session.commit()

            return redirect(url_for("main_home"))

        @self.app.errorhandler(404)
        def main_404(e): return "Page not found - i.e. you made a mistake"

        @self.app.errorhandler(500)
        def main_500(e): return "Server go boom - i.e. I made a mistake"

    def initPages_auth(self):
        @self.app.route("/login/")
        def auth_login():
            if current_user.is_authenticated:
                return redirect(url_for("main_home"))
            return render_template("login.html")

        @self.app.route("/login/", methods=["post"])
        def auth_login_post():
            username = request.form.get("username")
            password = request.form.get("password")
            remember = True if request.form.get('remember') else False

            user = self.User.query.filter_by(user_id=username).first()

            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('auth_login'))

            login_user(user,remember=remember)
            return redirect(url_for("main_home"))

        @self.app.route("/signup/")
        def auth_signup():
            if current_user.is_authenticated:
                return redirect(url_for("main_home"))
            return render_template("signup.html")

        @self.app.route("/signup/", methods=["post"])
        def auth_signup_post():
            username=request.form.get("username")
            password1=request.form.get("password")
            password2=request.form.get("password-repeat")

            verifyOutput=self.verifyField(username,"Username",canHaveSpecialChar=False)

            if len(verifyOutput) > 0:
                flash(verifyOutput)
                return redirect(url_for("auth_signup"))

            verifyOutput=self.verifyField(password1,"Password",minLen=8)

            if len(verifyOutput) > 0:
                flash(verifyOutput)
                return redirect(url_for("auth_signup"))

            if password1!=password2:
                flash("Passwords do not match")
                return redirect(url_for("auth_signup"))

            user = self.User.query.filter_by(user_id=username).first()

            if user:
                flash("That username is already in use")
                return redirect(url_for("auth_signup"))

            self.createUser(username,password1)

            return redirect(url_for("auth_login"))

        @self.app.route("/logout/")
        @login_required
        def auth_logout():
            logout_user()
            return redirect(url_for("auth_login"))

    def getBirdDictForFlash(self):
        query=self.User.query.filter_by(user_id=current_user.user_id).first()
        out={
            "robin":query.robin,
            "blackbird":query.blackbird,
            "pigeon":query.pigeon,
            "magpie":query.magpie,
            "blue tit":query.blue_tit,
            "thrush":query.thrush,
            "wren":query.wren,
            "starling":query.starling,
        }
        return {k:v for k,v in sorted(out.items(), key=lambda item: item[1])}

    def createUser(self,u,p):
        newUser = self.User(
            user_id=u,
            password=generate_password_hash(p, method='sha256'),
            robin=0,
            blackbird=0,
            pigeon=0,
            magpie=0,
            blue_tit=0,
            thrush=0,
            wren=0,
            starling=0
        )

        self.db.session.add(newUser)
        self.db.session.commit()

    def verifyField(self,field,fieldName,mustHaveChar=True,minLen=3,canHaveSpace=False,canHaveSpecialChar=True):
        specialChar="%&{}\\<>*?/$!'\":@+`|="

        if type(field) != str: Exception("HEY! that's not a string?")

        if len(field) == 0 and mustHaveChar: return f"{fieldName} is not filled out."
        if len(field) < minLen: return f"{fieldName} must be greater than {minLen-1} characters."
        if not canHaveSpace and " " in field: return f"{fieldName} cannot contain spaces."
        if not canHaveSpecialChar:
            for char in specialChar:
                if char in field:
                    return f"{fieldName} cannot contain '{char}'"

        return ""

if __name__ == "__main__":
    RSBPBirdwatchSite("0.0.0.0",8080)
