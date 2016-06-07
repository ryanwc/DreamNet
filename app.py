import os, webapp2, jinja2, re
from webapp2 import redirect_to
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
	autoescape=True, auto_reload=True)
jinja_env.globals['url_for'] = webapp2.uri_for


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

## need to refactor this for modules
# define the dream post
class Dream(db.Model):
	#required = true
	username = db.StringProperty()
	subject = db.StringProperty()
	content = db.TextProperty()
	#should be datetime
	# auto now add
	time_dreamt = db.TextProperty()
	time_posted = db.TextProperty()
	places = db.StringProperty()
	people = db.StringProperty()
	emotions = db.StringProperty()
	lucidity = db.StringProperty()
	lucidReason = db.StringProperty()
	control = db.StringProperty()
	enjoyability = db.StringProperty()

	'''
	def render(self):
		self._render_text=self.content.replace("\n", "<br>")
		return render_str("po")
	'''

# set signin regexes and validators
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
	return EMAIL_RE.match(email)

# define template servers
class Home(Handler):
	def get(self):

		# to change
		authentication = None
		username = self.request.get("username")

		dreams = Dream.all().order('time_posted')

		self.render("home.html", username=username,
			authentication=authentication, dreams=dreams)

class NewDream(Handler):
	def get(self):

		self.render("newdream.html", dreamDict=None, messages=None)

	def post(self):

		dreamDict = {}
		# to change
		dreamDict["subject"] = self.request.get("subject")
		dreamDict["content"] = self.request.get("content")

		dreamDict["time_dreamt"] = "test"
		dreamDict["time_posted"] = "test"
		dreamDict["places"] = "test"
		dreamDict["people"] = "test"
		dreamDict["emotions"] = "test"
		dreamDict["lucidity"] = "test"
		dreamDict["lucidReason"] = "test"
		dreamDict["control"] = "test"
		dreamDict["enjoyability"] = "test"

		messages = {}

		if dreamDict["subject"]:
			if len(dreamDict["subject"]) < 30:
				messages["subject"] = {"message": "Subject OK",
							 		   "validity": "valid"}
			else:
				messages["subject"] = {"message": "Subject invalid",
									   "validity": "invalid"}		
		else:
			messages["subject"] = {"message": "Please provide a subject",
								   "validity": "invalid"}

		if dreamDict["content"]:
			if len(dreamDict["content"]) < 10000:
				messages["content"] = {"message": "Content OK",
						 			   "validity": "valid"}
			else:
				messages["content"] = {"message": "Content invalid",
						 			   "validity": "invalid"}	
		else:
			messages["content"] = {"message": "Please provide content",
								   "validity": "invalid"}

		messages["time_dreamt"] = {"message": "OK",
							    "validity": "valid"}
		messages["time_posted"] = {"message": "OK",
							    "validity": "valid"}
		messages["places"] = {"message": "OK",
							    "validity": "valid"}
		messages["people"] = {"message": "OK",
							    "validity": "valid"}
		messages["emotions"] = {"message": "OK",
							    "validity": "valid"}
		messages["lucidity"] = {"message": "OK",
							    "validity": "valid"}
		messages["lucidReason"] = {"message": "OK",
							    "validity": "valid"}
		messages["control"] = {"message": "OK",
							    "validity": "valid"}
		messages["enjoyability"] = {"message": "OK",
							    "validity": "valid"}

		for attr in dreamDict:
			if messages[attr]["validity"] == "invalid":
				return self.render("newdream.html", dreamDict=dreamDict, 
					messages=messages)

		dream = Dream(**dreamDict)
		dream.put()

		return redirect_to("viewdream", id=str(dream.key().id()))

class Signin(Handler):
	def get(self):

		self.render("signin.html", values=None, messages=None)

	def post(self):

		name = self.request.get("name")
		password = self.request.get("password")
		verifyPassword = self.request.get("verifypassword")
		email = self.request.get("email")

		# holds message for user about input and 
		# whether input is valid or invalid
		messages = {}

		### CLEAN INPUT WITH BLEACH TOO IF PRODUCTION

		# ideally refactor so all helper validation functions

		# name must be only alphabetic chars
		if name:
			if valid_username(name):
				messages["name"] = {"message": "Name OK",
							 		"validity": "valid"}
			else:
				messages["name"] = {"message": "Name invalid",
									"validity": "invalid"}		
		else:
			messages["name"] = {"message": "Please provide a name",
								"validity": "invalid"}

		# not the "best" password but could improve for production
		if password:
			if valid_password(password):
				messages["password"] = {"message": "Password OK",
						 				"validity": "valid"}
			else:
				messages["password"] = {"message": "Password invalid",
						 				"validity": "invalid"}	
		else:
			messages["password"] = {"message": "Please provide a pasword",
								    "validity": "invalid"}

		# verifypassword must match password
		if verifyPassword:
			if not verifyPassword == password:
				messages["verifypassword"] = \
					{"message": "Verify password does not match password",
		 			 "validity": "invalid"}
		 	else:
				messages["verifypassword"] = {"message": "OK (password "+\
							"matches)", "validity": "valid"}
		else:
			messages["verifypassword"] = {"message": "Please verify password",
								    	  "validity": "invalid"}

		# email must be valid email
		# not the 'best' but a start
		if email:
			if valid_email(email):
				messages["email"] = {"message": "Email is valid",
									 "validity": "valid"}
			else:
				messages["email"] = {"message": "Email is invalid",
									 "validity": "invalid"}
		else:
			messages["email"] = {"message": "Please provide an email",
								 "validity": "invalid"}

		values = {}
		values["name"] = name
		values["password"] = password
		values["verifypassword"] = verifyPassword
		values["email"] = email

		for field in messages:
			if messages[field]["validity"] == "invalid":
				return self.render("signin.html", values=values, 
					messages=messages)

		return redirect_to("home", username=name)

class ViewDream(Handler):
	def get(self, id=None):
		dream = Dream.get_by_id(int(id))
		print dream

		self.render("viewdream.html", dream=dream)

# To get the ID of an entity you just created: obj.key().id()

app = webapp2.WSGIApplication(
		[webapp2.Route("/home", handler=Home, name="home"),
		 ("/signin", Signin),
		 webapp2.Route("/dream/view/<id>", handler=ViewDream, name="viewdream"),
		 webapp2.Route("/dream/new", handler=NewDream, name="newdream")],
		debug=True)


