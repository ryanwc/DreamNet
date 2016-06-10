import os, webapp2, jinja2, re, hashlib, hmac, random, string, random
from webapp2 import redirect_to
from google.appengine.ext import db
#import bleach third party lib?

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
# define entities

class User(db.Model):
	# what other unchanging properties?
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	#birthdate = db.DateProperty(required = True)
	#nationality = db.StringProperty(required = True)
	email = db.StringProperty(required = True)

class Dream(db.Model):
	#required = true
	user = db.ReferenceProperty(User,
							 	collection_name = "dreams")
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	#should be datetime
	# auto now add
	# what other properties do we want to keep? location? language?
	# need to balance easy to do form but get info
	date_dreamt = db.TextProperty(required = True)
	date_posted = db.TextProperty(required = True)
	genres = db.StringListProperty(required = True)
	places = db.StringListProperty(required = True)
	people = db.StringListProperty(required = True)
	emotions_during = db.StringListProperty(required = True)
	emotions_remembering = db.StringListProperty(required = True)
	lucidity = db.IntegerProperty(required = True)
	lucid_reason = db.StringProperty()
	control = db.IntegerProperty(required = True)
	enjoyability = db.IntegerProperty(required = True)
	awareness_level = db.IntegerProperty(required = True)

	## maybe not right, idea is to render \n as HTML breaks
	def render(self):
		self._render_text = self.content.replace("\n", "<br>")
		return render_str(self._render_text)


### helper functions

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
	salt = h.split(",")[1]
	return h == make_pw_hash(name, pw, salt)

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

SECRET = 'examplesecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

# allows for '|' in the value
def check_secure_val(h):
    li = h.split("|")
    HASH = li[len(li)-1]
    s = ""

    for x in range(len(li)-1):
        s += li[x]

        if x < (len(li)-2):
            s += "|"

    if hash_str(s) == HASH:
        return s
    else:
        return None

def getUserFromSecureCookie(username_cookie_val):

	username = None

	if username_cookie_val:
		username_cookie_val = check_secure_val(username_cookie_val)
		if username_cookie_val:
			username = username_cookie_val

	return username

# define template servers
class Home(Handler):
	def get(self):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))

		# set some vars based on username
		authentication = {}
		if username:
			# todo: implement signout
			authentication["link"] = "#"
			authentication["linkText"] = "Sign out"
		else:
			authentication["link"] = webapp2.uri_for("register")
			authentication["linkText"] = "Sign in or create profile"

		# get/set a cookie that tracks number of visits
		visits = 0
		visit_cookie_val = self.request.cookies.get("visits")

		if visit_cookie_val:
			visit_cookie_val = check_secure_val(visit_cookie_val)
			if visit_cookie_val:
				visits = int(visit_cookie_val)

		visits += 1

		visit_cookie_val = make_secure_val(str(visits))

		self.response.set_cookie("visits", visit_cookie_val)

		dreamQ = Dream.all().order("date_posted")
		dreams = []
		for dream in dreamQ.run():
			dreams.append(dream)

		self.render("home.html", username=username,
			authentication=authentication, dreams=dreams)

class NewDream(Handler):
	def get(self):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))

		if not username:
			return redirect_to("signin")

		self.render("newdream.html", dreamDict=None, messages=None)

	def post(self):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		users = User.all()
		users.filter("username =", username)
		user = users.get()

		if not username:
			return redirect_to("signin")

		dreamDict = {}
		# to change
		dreamDict["user"] = user
		dreamDict["title"] = self.request.get("title")
		dreamDict["content"] = self.request.get("content")
		dreamDict["genres"] = []
		dreamDict["date_dreamt"] = "test"
		dreamDict["date_posted"] = "test"
		dreamDict["places"] = []
		dreamDict["people"] = []
		dreamDict["emotions_during"] = []
		dreamDict["emotions_remembering"] = []
		dreamDict["lucidity"] = 0
		dreamDict["lucid_reason"] = ""
		dreamDict["control"] = 0
		dreamDict["enjoyability"] = 0
		dreamDict["awareness_level"] = 0

		messages = {}

		if dreamDict["title"]:
			if len(dreamDict["title"]) < 30:
				messages["title"] = {"message": "title OK",
							 		   "validity": "valid"}
			else:
				messages["title"] = {"message": "title invalid",
									   "validity": "invalid"}		
		else:
			messages["title"] = {"message": "Please provide a title",
								 "validity": "invalid"}

		if dreamDict["content"]:
			if len(dreamDict["content"]) < 50000:
				messages["content"] = {"message": "Content OK",
						 			   "validity": "valid"}
			else:
				messages["content"] = {"message": "Content invalid",
						 			   "validity": "invalid"}	
		else:
			messages["content"] = {"message": "Please provide content",
								   "validity": "invalid"}

		messages["user"] = {"message": "OK",
							"validity": "valid"}
		messages["date_dreamt"] = {"message": "OK",
							    "validity": "valid"}
		messages["date_posted"] = {"message": "OK",
							    "validity": "valid"}
		messages["genres"] = {"message": "OK",
							    "validity": "valid"}
		messages["places"] = {"message": "OK",
							    "validity": "valid"}
		messages["people"] = {"message": "OK",
							    "validity": "valid"}
		messages["emotions_during"] = {"message": "OK",
								       "validity": "valid"}
		messages["emotions_remembering"] = {"message": "OK",
							   			    "validity": "valid"}
		messages["lucidity"] = {"message": "OK",
							    "validity": "valid"}
		messages["lucid_reason"] = {"message": "OK",
							    "validity": "valid"}
		messages["control"] = {"message": "OK",
							    "validity": "valid"}
		messages["enjoyability"] = {"message": "OK",
							    "validity": "valid"}
		messages["awareness_level"] = {"message": "OK",
							    	   "validity": "valid"}

		for attr in dreamDict:
			if messages[attr]["validity"] == "invalid":
				return self.render("newdream.html", dreamDict=dreamDict, 
					messages=messages)

		dream = Dream(**dreamDict)
		dream.put()

		return redirect_to("viewdream", id=str(dream.key().id()))

class Register(Handler):
	def get(self):

		self.render("register.html", values=None, messages=None)

	def post(self):

		name = self.request.get("name")
		password = self.request.get("password")
		verifyPassword = self.request.get("verifypassword")
		email = self.request.get("email")

		# holds message for user about input and 
		# whether input is valid or invalid
		messages = {}

		### CLEAN INPUT WITH BLEACH OR SIMILAR IF PRODUCTION

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

		saltedpasshash = make_pw_hash(name, password)

		user = User(username=name, password=saltedpasshash, email=email)
		user.put()

		# if more than one with this email or user name, delete this one
		# and return invalid. hacky workaround of seemingly bad google 
		# datastore support for unique entity values
		# (username and email should be unique)
		users = User.all()
		users.filter("username =", user.username)
		numSameUsername = 0
		for u in users.run():
			numSameUsername += 1
			if numSameUsername > 1:
				messages["name"] = {"message": "Name already taken",
									"validity": "invalid"}
				user.delete()
			break

		users = User.all()
		users.filter("email =", user.email)
		numSameEmail = 0
		for u in users.run():
			numSameEmail += 1
			if numSameEmail > 1:
				messages["email"] = {"message": "Email already in use",
									 "validity": "invalid"}
				user.delete()
				break

		for field in messages:
			if messages[field]["validity"] == "invalid":
				return self.render("register.html", values=values, 
					messages=messages)

		username_cookie_val = make_secure_val(user.username)

		response = redirect_to("home")
		response.set_cookie("username", username_cookie_val)
		return response

class Signin(Handler):
	def get(self):

		self.render("signin.html", values=None, messages=None)

	def post(self):

		name = self.request.get("name")
		password = self.request.get("password")

		# holds message for user about input and 
		# whether input is valid or invalid
		messages = {}

		if name:
			users = User.all()
			users.filter("username =", name)
			user = users.get()
			if user:
				messages["name"] = {"message": "",
							 		"validity": "valid"}
				if password:
					saltedpasshash = user.password
					if valid_pw(user.username, password, saltedpasshash):
						messages["password"] = {"message": "",
									 		    "validity": "valid"}
					else:
						messages["password"] = {"message": "Password incorrect",
				 							    "validity": "invalid"}	
				else:
						messages["password"] = {"message": "Enter password",
				 							    "validity": "invalid"}	
			else:
				messages["name"] = {"message": "Username does not exist",
									"validity": "invalid"}	
				messages["password"] = {"message": "",
									    "validity": "invalid"}
		else:
			messages["name"] = {"message": "Please provide a name",
								"validity": "invalid"}
			messages["password"] = {"message": "",
								    "validity": "invalid"}

		values = {}
		values["name"] = name
		values["password"] = password

		for field in messages:
			if messages[field]["validity"] == "invalid":
				return self.render("signin.html", values=values, 
					messages=messages)


		username_cookie_val = make_secure_val(user.username)

		response = redirect_to("home")
		response.set_cookie("username", username_cookie_val)
		return response

class ViewDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		print username
		print dream.user.username

		self.render("viewdream.html", dream=dream, username=username)

class EditDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		if not username:
			return redirect_to("signin")
		elif username != dream.username:
			return redirect_to("home")

		self.render("editdream.html", dream=dream)

	def post(self, id=None):

		self.render("editdream.html", dream=dream)

class DeleteDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		if not username:
			return redirect_to("signin")
		elif username != dream.username:
			return redirect_to("home")

		self.render("deletedream.html", dream=dream)

	def post(self, id=None):

		self.render("deletedream.html", dream=dream)

class LikeDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		if not username:
			return redirect_to("signin")

		dream.awareness_level += 1

		return redirect_to("viewdream", id=id)

class About(Handler):
	def get(self):

		self.render("about.html")

class Logout(Handler):
	def get(self):
		response = redirect_to("signin")
		response.set_cookie("username", "")
		return response


# To get the ID of an entity you just created: obj.key().id()

app = webapp2.WSGIApplication(
		[webapp2.Route("/home", handler=Home, name="home"),
		 webapp2.Route("/about", handler=About, name="about"),
		 webapp2.Route("/register", handler=Register, name="register"),
		 webapp2.Route("/signin", handler=Signin, name="signin"),
		 webapp2.Route("/logout", handler=Logout, name="logout"),
		 webapp2.Route("/dream/view/<id>", handler=ViewDream, name="viewdream"),
		 webapp2.Route("/dream/like/<id>", handler=LikeDream, name="likedream"),
		 webapp2.Route("/dream/edit/<id>", handler=EditDream, name="editdream"),
		 webapp2.Route("/dream/delete/<id>", handler=DeleteDream, name="deletedream"),
		 webapp2.Route("/dream/new", handler=NewDream, name="newdream")],
		debug=True)


