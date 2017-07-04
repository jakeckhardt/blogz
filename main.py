from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "#someSecretString"

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(120), unique=True)
	password=db.Column(db.String(120))
	blogs=db.relationship('Blog', backref="owner")

	def __init__(self, username, password):
		self.username = username
		self.password = password

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(120))
	owner_id=db.Column(db.Integer, db.ForeignKey("user.id"))

	def __init__(self, title, body, owner):
	    self.title = title
	    self.body = body
	    self.owner = owner


def getBlogList():
    return Blog.query.all()

def getUserList():
	return User.query.all()


@app.before_request
def require_login():
	allowed_routes = ["logon", "signup", "index", "blog"]
	if request.endpoint not in allowed_routes and "username" not in session:
		return redirect("/logon")


@app.route("/blog")
def blog():
	entry_id = request.args.get("id")
	user_id = request.args.get("user")


	if user_id != None:
		session["user_id"] = user_id

	if "user_id" in session:
		user_name = User.query.filter_by(id=user_id).first()
		user_name = user_name.username
		user_entries=Blog.query.filter_by(owner_id=user_id).all()
		del session["user_id"]
		return render_template("user_entries.html", name=user_name, user_entries=user_entries)

	if entry_id != None:
		session["identification"] = entry_id

	if "identification" in session:
		blog_item = session["identification"]
		blog_item = Blog.query.filter_by(id=blog_item).first()
		title = blog_item.title
		body = blog_item.body
		user_id = blog_item.owner_id
		user = User.query.filter_by(id=user_id).first()
		user = user.username
		del session["identification"]

		return render_template("single.html", title = title, body = body, user_id=user_id, user=user)

	return render_template("blog.html", blog = getBlogList(), entry_id=entry_id, users=getUserList())


@app.route("/newpost", methods=["POST"])
def update():
	title = request.form["title"]
	body = request.form["body"]
	owner = User.query.filter_by(username=session["username"]).first()

	title_error = ""
	body_error = ""

	if title == "" or body == "":
		if title == "":
			title_error = "Please enter a title"

		if body == "":
			body_error = "Please enter a body"
		
		return render_template("add.html", title=title, body=body, title_error=title_error, body_error=body_error)

	else:
		entry = Blog(title, body, owner)
		db.session.add(entry)
		db.session.commit()
		identification = Blog.query.filter_by(title=title).first()
		session["identification"] = identification.id
		return redirect("/blog?id=" + str(session["identification"]))



@app.route("/newpost")
def newpost():
	return render_template("add.html", title = "", body = "", title_error="", body_error="")



@app.route("/signup", methods=["POST", "GET"])
def signup():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		v_password = request.form["v_password"]
		user = User.query.filter_by(username=username).first()

		username_error=""
		password_error=""
		v_password_error=""

		if not user and len(password) > 3 and password == v_password:
			new_user = User(username, password)
			db.session.add(new_user)
			db.session.commit()
			session["username"] = username
			return redirect("/newpost")

		if username == "":
			username_error = "Please enter a username"
			username = ""

		elif len(username) < 3:
			username_error = "Username must be more than three charactors"
			username = ""

		elif user:
			username_error = "Username already exists"
			username = ""

		if password == "":
			password_error = "Please enter password"

		elif len(password) < 3:
			password_error = "Password must be more than three charactors"

		elif password != v_password:
			v_password_error = "Passwords did not match"

		return render_template("signup.html", username=username, username_error=username_error, password_error=password_error, v_password_error=v_password_error)

	return render_template("signup.html")


@app.route("/logout")
def logout():
	del session["username"]
	return redirect("/blog")


@app.route("/logon", methods=["POST", "GET"])
def logon():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		user = User.query.filter_by(username=username).first()

		username_error=""
		password_error=""

		if user and user.password == password:
			session["username"] = username
			return redirect("/newpost")

		if username == "":
			username_error = "Please enter a username"
			username = ""

		elif not user:
			username_error = "Username does not exist"
			username= ""

		if password == "":
			password_error = "Please enter a password"

		return render_template("login.html", username=username, username_error=username_error, password_error=password_error)

	return render_template("login.html")



@app.route("/")
def index():
	user_id = request.args.get("user")

	return render_template("index.html", user = getUserList(), user_id=user_id)

if __name__ == "__main__":
	app.run()
