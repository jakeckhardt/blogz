from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog_1:blog@localhost:8889/build-a-blog_1'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "#someSecretString"

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(120))

	def __init__(self, title, body):
	    self.title = title
	    self.body = body


def getBlogList():
    return Blog.query.all()

@app.route("/blog")
def blogged():
	entryId = request.args.get("id")

	if entryId != None:
		session["identification"] = entryId

	if "identification" in session:
		blogItem = session["identification"]
		blogItem = Blog.query.filter_by(id=blogItem).first()
		title = blogItem.title
		body = blogItem.body
		del session["identification"]

		return render_template("single.html", title = title, body = body)

	return render_template("blog.html", blog = getBlogList(), entryId=entryId)


@app.route("/newpost", methods=["POST"])
def update():
	title = request.form["title"]
	body = request.form["body"]

	title_error = ""
	body_error = ""

	if title == "" or body == "":
		if title == "":
			title_error = "Please enter a title"

		if body == "":
			body_error = "Please enter a body"
		
		return render_template("add.html", title=title, body=body, title_error=title_error, body_error=body_error)

	else:
		entry = Blog(title, body)
		db.session.add(entry)
		db.session.commit()
		identification = Blog.query.filter_by(title=title).first()
		session["identification"] = identification.id
		return redirect("/blog?id=" + str(session["identification"]))



@app.route("/newpost")
def index():
	return render_template("add.html", title = "", body = "", title_error="", body_error="")

if __name__ == "__main__":
	app.run()
