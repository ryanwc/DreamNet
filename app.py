import os, webapp2, jinja2, re, hashlib, hmac, random, datetime, json
from datetime import date
import string, random, cPickle as pickle
from webapp2 import redirect_to
from google.appengine.ext import db
# import bleach third party lib?

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
	useful_dreams = db.StringProperty(required = True, multiline = True)

class Dream(db.Model):
	# what other properties do we want to keep? 
	# current country? country of origin? primary language? gender? age?
	user = db.ReferenceProperty(User,
							 	collection_name = "dreams")
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	date_dreamt = db.DateProperty(required = True)
	date_posted = db.DateTimeProperty(auto_now_add=True)
	lucidity = db.BooleanProperty(required = True)
	lucid_length = db.StringProperty()
	lucid_reason = db.StringProperty()
	control = db.IntegerProperty(required = True)
	enjoyability = db.IntegerProperty(required = True)
	awareness_level = db.IntegerProperty(required = True)
	aware_users = db.StringProperty(multiline = True)

	## maybe not right, idea is to render \n as HTML breaks
	def render(self):
		self._render_text = self.content.replace("\n", "<br>")
		return render_str(self._render_text)

class TagGroup(db.Model):
	# types, places, people, things, emotions, sensations
	name = db.StringProperty(required = True)

class TagName(db.Model):
	name = db.StringProperty(required = True)
	group = db.ReferenceProperty(TagGroup,
							     collection_name = "tag_names")

class Tag(db.Model):
	dream = db.ReferenceProperty(Dream,
								 collection_name = "tags")
	name = db.ReferenceProperty(TagName,
						    	collection_name = "tags")

### some helpful globals
### these could be a separate entity instead
# need to resolve collisions by asking user is it this or this
# need to say "havent seen that yet"
# need to say "what the fuck is that crazy person behind me laughing at"
TAGS = {}

types = ["flying", "falling", "nudity", "sex", "nightmare", "being chased",
		 "paralysis", "trapped", "difficult to move", "eating", "death",
		 "violence", "school/classroom/exam", "aquatic", "demonic",
		 "religious", "angelic", "fantasy", "sci-fi", "romantic", "comedy",
		 "missed/late to appointment/event", "travel", "futuristic", 
		 "in the past", "light", "darkness"]

people = ["mother", "father", "brother", "sister", "cousin", "aunt", "uncle",
		  "son", "daughter", "neice", "nephew", "cousin", "grandfather",
		  "grandmother", "grandson", "granddaughter", "mother-in-law",
		  "father-in-law", "brother-in-law", "sister-in-law", "son-in-law",
		  "daughter-in-law", "boss/manager", "direct report", "employee", 
		  "coworker", "wife", "girlfriend", "husband", "boyfriend", 
		  "best friend", "friend", "aquaintance", "business partner", "crush",
		  "person from childhood", "person from highschool", 
		  "person from college", "teacher/professor"]

places = ["vaccuum/emptiness", "foreign country", "countryside", "kitchen",
		  "bedroom", "livingroom", "bathroom", "hallway", "ruins", 
		  "military base", "heaven", "hell", "beach", "house", "road/highway",
		  "ocean", "lake", "river", "swamp", "desert", "glacier", "rainforest",
		  "forest", "boat", "cave", "office building", "abandoned building",
		  "stadium", "open field", "farm", "mountain", "airport", "school",
		  "classroom", "hospital", "doctor's office", "science facility",
		  "outer space", "spaceship", "alien world"]

things = ["bowl", "door", "hat", "ghost", "caterpillar", "dog", "chair",
		  "watch", "clock", "staircase", "flag", "gun", "knife", "car",
		  "boat", "airplane", "spoon", "fork", "table", "wall", "present",
		  "strawberry", "food", "blueberry"]

emotions = ["happiness", "ecstacy", "sadness", "sorrow/grief", "depression",
			"fear", "terror", "disgust", "anger", "indignation", "hatred",
			"love", "anxiety", "relief", "shame", "pride", "envy", "goodwill", 
			"confusion", "clarity", "stress", "relaxation", "caution", 
			"rashness", "kindness", "pity", "cruelty", "courage", "cowardice",
			"wonder", "boredom"]

sensations = ["pain", "discomfort", "pleasure", "orgasm", "taste", "color",
			  "red", "yellow", "green", "blue", "white", "black", "violet", 
			  "orange", "pink", "brown", "purple", "sour", "sweet", "salty",
			  "bitter", "umami", "comfort", "heat" "cold", "numbness"]

TAGS['type'] = types
TAGS['person'] = people
TAGS['place'] = places
TAGS['thing'] = things
TAGS['emotion'] = emotions
TAGS['sensation'] = sensations

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
	def get(self, page=1):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))

		'''
		for group in TAGS:
			group = TagGroup(name=group)
			group.put()
			for tagname in TAGS[group.name]:
				tag = TagName(name=tagname, group=group)
				tag.put()
		'''

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

		dreamQ = Dream.all()
		#dreamQ.order("date_posted")
		dreams = []
		start = (int(page)-1)*10
		for dream in dreamQ.run(offset=start, limit=start+10):
			dreams.append(dream)

		self.render("home.html", username=username, dreams=dreams)

class NewDream(Handler):
	def get(self):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))

		if not username:
			return redirect_to("signin")

		tagsQ = TagName.all()
		tagsQ.order("name")
		groupsQ = TagGroup.all()
		tagGroupToNames = {}
		tagNameToGroup = {}

		for tagGroup in groupsQ:
			tagGroupToNames[tagGroup.name] = []

		for tag in tagsQ:
			tagNameToGroup[tag.name] = tag.group.name
			tagGroupToNames[tag.group.name].append(tag.name)

		self.render("newdream.html", dreamDict=None, 
					messages=None, tagGroupToNames=json.dumps(tagGroupToNames),
					tagNameToGroup=json.dumps(tagNameToGroup))

	def post(self):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		users = User.all()
		users.filter("username =", username)
		user = users.get()

		if not username:
			return redirect_to("signin")

		dreamDict = {}
		messages = {}

		dreamDict["user"] = user
		messages["user"] = {"message": "User OK",
						    "validity": "valid"}

		dreamDict["date_dreamt"] = self.request.get("datedreamt")
		## change for international versions?
		if dreamDict["date_dreamt"]:
			date_dreamt_string = str(dreamDict["date_dreamt"])
			date_dreamt_array = re.split(r"[^0-9]", date_dreamt_string)

			year = int(date_dreamt_array[0])
			month = int(date_dreamt_array[1])
			day = int(date_dreamt_array[2])

			date_dreamt = None

			try:
				date_dreamt = datetime.date(year, month, day)
				print "date dreamt succeeded: "
				print date_dreamt
			except ValueError:
				messages["date_dreamt"] = {"message": "Please fix the date formatting (mm/dd/yyyy)",
							 	 	       "validity": "invalid"}

			if date_dreamt:
				dreamDict["date_dreamt"] = date_dreamt
				messages["date_dreamt"] = {"message": "Date dreamt OK",
			 	 	     "validity": "valid"}
		else:
			messages["date_dreamt"] = {"message": "Please provide the day you had the dream",
							 	 	   "validity": "invalid"}		

		dreamDict["date_posted"] = datetime.datetime.now()
		messages["date_posted"] = {"message": "Date posted OK",
						    	   "validity": "valid"}

		dreamDict["lucidity"] = self.request.get("lucidity")
		if dreamDict["lucidity"]:
			
			if (dreamDict["lucidity"] != "True" and 
				dreamDict["lucidity"] != "False"):

				messages["lucidity"] = {"message": "Answer 'Yes' or 'No'",
							 	 	    "validity": "invalid"}
			else:
				messages["lucidity"] = {"message": "Lucidity answer OK",
							 	 	    "validity": "valid"}	

			if dreamDict["lucidity"] == "True":

				dreamDict["lucid_reason"] = self.request.get("lucidreason")

				# would it be best to have the forms return the text instead of a number code?
				# originally thought code best so backend could be independent of front end text
				if (dreamDict["lucid_reason"] == "-1" or 
					dreamDict["lucid_reason"] == None or
					dreamDict["lucid_reason"] == ""):

					messages["lucid_reason"] = {"message": "Please enter how you became aware you were dreaming",
							 	 	    		"validity": "invalid"}	
				elif (dreamDict["lucid_reason"] == "WILD" or 
					  dreamDict["lucid_reason"] == "reality check" or
					  dreamDict["lucid_reason"] == "dream sign" or
					  dreamDict["lucid_reason"] == "off" or
					  dreamDict["lucid_reason"] == "something else"):

					messages["lucid_reason"] = {"message": "Reason selection OK",
							 	 	    		"validity": "valid"}	

					if dreamDict["lucid_reason"] == "something else":

						dreamDict["something_else"] = self.request.get("somethingelse")

						if dreamDict["something_else"]:
							if len(dreamDict["something_else"]) < 301:
								messages["something_else"] = {"message": "Custom reason for awareness OK",
								 	 	    			  	  "validity": "valid"}			
							else:
								messages["something_else"] = {"message": "Custom reason for awareness is too long (300 char max)",
								 	 	    			  	  "validity": "invalid"}			
						else:
							messages["something_else"] = {"message": "Please enter your custom reason for becomming aware that you were dreaming",
								 	 	    			  "validity": "invalid"}		

				dreamDict["lucid_length"] = self.request.get("lucidlength")

				# would it be best to have the forms return the text instead of a number code?
				# originally thought code best so backend could be independent of front end text
				if (dreamDict["lucid_length"] == "very short" or 
					dreamDict["lucid_length"] == "in between" or
					dreamDict["lucid_length"] == "entire"):

					messages["lucid_length"] = {"message": "Lucid length OK",
							 	 	    		"validity": "valid"}
				else:

					messages["lucid_length"] = {"message": "Please indicate how long you remained aware you were dreaming after becoming aware",
							 	 	    		"validity": "invalid"}	
		else:
			messages["lucidity"] = {"message": "Please indicate whether you were aware you were dreaming at any point during the dream",
							 	 	"validity": "invalid"}	

		dreamDict["control"] = self.request.get("control")
		if dreamDict["control"]:

			try:

				control = int(dreamDict["control"])

				if (control < 0 or
					control > 10):

					messages["control"] = {"message": "Control level was invalid.  Use the slider to set control level",
							 		 	   "validity": "invalid"}
				else:
					messages["control"] = {"message": "Control level OK.",
							 		 	   "validity": "valid"}
			except ValueError:

				messages["control"] = {"message": "Control level was invalid.  Use the slider to set control level",
							 	 	   "validity": "invalid"}	
		else:
			messages["control"] = {"message": "Please use the slider to set the level of control you felt you had during the dream",
							 	   "validity": "invalid"}	

		dreamDict["enjoyability"] = self.request.get("enjoyability")
		if dreamDict["enjoyability"]:

			try:

				enjoyability = int(dreamDict["enjoyability"])

				if (enjoyability < 0 or
					enjoyability > 10):

					messages["enjoyability"] = {"message": "Enjoyability was invalid.  Use the slider to set enjoyability",
							 		 	        "validity": "invalid"}
				else:
					messages["enjoyability"] = {"message": "Enjoyability OK",
							 		 	        "validity": "valid"}

			except ValueError:

				messages["enjoyability"] = {"message": "Enjoyability level was invalid.  Use the slider to set enjoyability level",
							 	 	        "validity": "invalid"}	
		else:
			messages["enjoyability"] = {"message": "Please use the slider to enter how enjoyable you think the dream was",
							 	 		"validity": "invalid"}			
		
		dreamDict["title"] = self.request.get("title")
		if dreamDict["title"]:

			if len(dreamDict["title"]) < 51:
				messages["title"] = {"message": "Title OK",
							 	 	 "validity": "valid"}	
			else:
				messages["title"] = {"message": "Title was too long (50 char max)",
							 	 	 "validity": "invalid"}		
		else:
			messages["title"] = {"message": "Please enter a title for the dream",
							 	 "validity": "invalid"}	

		dreamDict["description"] = self.request.get("description")
		if dreamDict["description"]:

			if len(dreamDict["description"]) < 301:
				messages["description"] = {"message": "Description OK",
							 	 	 	   "validity": "valid"}	
			else:
				messages["description"] = {"message": "Description was too long (301 char max)",
							 	 	 		"validity": "invalid"}		
		else:
			messages["description"] = {"message": "Please enter a description for the dream",
							 	 	   "validity": "invalid"}

		inputTags = self.request.get("dreamtags")
		### get dream tags with regexes (values of each button)
		hasTypeTag = False
		dreamDict["dream_tags"] = {}
		if inputTags:

			inputTags_array = inputTags.split(",")

			# validate each name|value pair, stopping before last array entry 
			# due to "," being the last character in inputTags when splitting on ","
			for i in range(0, len(inputTags_array)-1):

				inputTag = inputTags_array[i]

				tag_array = inputTag.split("|")

				if len(tag_array) != 2:
					messages["dream_tags"] = {"message": "One of the tags contains an illegal '|' character",
							 	 	 		  "validity": "invalid"}
					break

				tag_name = tag_array[0]
				tag_group = tag_array[1]

				# check if already exists (but do not add yet)
				# think have to all() each time thru for loop but not sure, playing safe
				existingTagNames = TagName.all()
				existingTagName = existingTagNames.filter("name =", tag_name).get()
				if existingTagName:
					if tag_group != existingTagName.group.name:
						messages["dream_tags"] = {"message": "Tag '"+tag_name+"' has the wrong tag kind.  Try removing and re-adding it.",
							 	 	 			  "validity": "invalid"}
						break				

				if len(tag_name) < 1:
					messages["dream_tags"] = {"message": "One of the tags has no name",
							 	 	 			"validity": "invalid"}
					break
				elif len(tag_name) > 50:
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' name is too long (max 50 chars)",
		 	 	 							  "validity": "invalid"}
					break
				elif (re.search(r'[1234567890~!@#\$\+=%\^&\*\()<>,\./\?;:\[\]\{}\|_\\]', tag_name)):
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' has an illegal character",
		 	 	 							  "validity": "invalid"}
					break
				elif (re.search(r'  ', tag_name)):
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' cannot contain two spaces in a row",
		 	 	 							  "validity": "invalid"}
					break
				elif (re.search(r"''", tag_name)):
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' cannot contain two apostrophes in a row",
		 	 	 							  "validity": "invalid"}
					break
				elif (re.search(r'--', tag_name)):
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' cannot contain two hyphens in a row",
		 	 	 							  "validity": "invalid"}
					break

				if (tag_group not in TAGS):
					messages["dream_tags"] = {"message": "tag '"+tag_name+"' has an invalid tag group ('"+tag_group+"')",
		 	 	 							  "validity": "invalid"}
		 	 	 	break
				elif tag_group == "type":
					hasTypeTag = True

				dreamDict["dream_tags"][tag_name] = tag_group

		 	if not hasTypeTag:
				messages["dream_tags"] = {"message": "Please enter at least one 'type' tag",
							 	 	  	  "validity": "invalid"}	
			
			# if made it this far without setting the message, the tags are valid
			if "dream_tags" not in messages:
				messages["dream_tags"] = {"message": "Dream tags OK",
	 	 	 							  "validity": "valid"}			 		
		else:
			messages["dream_tags"] = {"message": "Please enter some tags, including at least one 'type' tag",
							 	 	  "validity": "invalid"}			

		dreamDict["content"] = self.request.get("content")
		if dreamDict["content"]:
			if len(dreamDict["content"]) < 50001:
				messages["content"] = {"message": "Dream narrative OK",
						 			   "validity": "valid"}
			else:
				messages["content"] = {"message": "Dream narrative was too long (50000 char max)",
						 			   "validity": "invalid"}	
		else:
			messages["content"] = {"message": "Please provide a narrative of what happened in the dream",
								   "validity": "invalid"}

		dreamDict["awareness_level"] = 0
		aware_users = "None yet"

		# get existing tags in case redirect to form
		tagsQ = TagName.all()
		tagsQ.order("name")
		groupsQ = TagGroup.all()
		tagGroupToNames = {}
		tagNameToGroup = {}

		for tagGroup in groupsQ:
			tagGroupToNames[tagGroup.name] = []

		for tag in tagsQ:
			tagNameToGroup[tag.name] = tag.group.name
			tagGroupToNames[tag.group.name].append(tag.name)

		for attr in dreamDict:
			print attr
			print dreamDict[attr]
			print type(dreamDict[attr])
			if attr in messages:
				if messages[attr]["validity"] == "invalid":
					return self.render("newdream.html", dreamDict=dreamDict, 
						messages=messages, tagGroupToNames=json.dumps(tagGroupToNames),
						tagNameToGroup=json.dumps(tagNameToGroup))

		# set values for datastore (some cannot be string)
		if dreamDict["lucidity"] == "True":
			dreamDict["lucidity"] = True
		else:
			dreamDict["lucidity"] = False

		dreamDict["control"] = int(dreamDict["control"])
		dreamDict["enjoyability"] = int(dreamDict["enjoyability"])

		dream = Dream(**dreamDict)
		dream.put()

		# create each dream tag object
		# (consists of an id, a reference to a dream, and a reference to a tag name)
		for tag_name in dreamDict["dream_tags"]:
			existingTagName = TagName.all().filter("name =", tag_name).get()

			tag_group = dreamDict["dream_tags"][tag_name]
			tagGroupObj = TagGroup.all().filter("name =", tag_group).get()

			assert tagGroupObj

			if existingTagName == None:
				tagNameObj = TagName(name=tag_name, group=tagGroupObj)
				tagNameObj.put()
			else:
				tagNameObj = existingTagName

			dreamTag = Tag(dream=dream, name=tagNameObj)

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

		useful_dreams = {}

		user = User(username=name, password=saltedpasshash, 
					email=email, useful_dreams=pickle.dumps(useful_dreams))
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

		response = redirect_to("home", page=1)
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

		response = redirect_to("home", page=1)
		response.set_cookie("username", username_cookie_val)
		return response

class ViewDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		self.render("viewdream.html", dream=dream, username=username)

class EditDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		dream = Dream.get_by_id(int(id))

		if not username:
			return redirect_to("signin")
		elif username != dream.username:
			return redirect_to("home", page=1)

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
			return redirect_to("home", page=1)

		self.render("deletedream.html", dream=dream)

	def post(self, id=None):

		self.render("deletedream.html", dream=dream)

class LikeDream(Handler):
	def get(self, id=None):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))
		users = User.all()
		user = users.filter("username =", username).get()

		dream = Dream.get_by_id(int(id))

		if not username:
			return redirect_to("viewdream", id=id)

		if user.key().id() == dream.user.key().id():
			return redirect_to("viewdream", id=id)

		aware_users = pickle.loads(str(dream.aware_users))
		useful_dreams = pickle.loads(str(user.useful_dreams))

		if (not user.key().id() in aware_users and 
			not long(id) in useful_dreams):

			dream.awareness_level += 1

			aware_users[user.key().id()] = True
			dream.aware_users = pickle.dumps(aware_users)
			dream.put()

			useful_dreams[long(id)] = True
			user.useful_dreams = pickle.dumps(useful_dreams)
			user.put()


		return redirect_to("viewdream", id=id)

class About(Handler):
	def get(self):

		self.render("about.html")

class Logout(Handler):
	def get(self):
		response = redirect_to("signin")
		response.set_cookie("username", "")
		return response

# Ajax handlers

class TagHandler(Handler):
    def post(self):
		existingTagsQ = Tag.all()
		existingTagsQ.order("name")
		existingTags = []

		for existingTag in existingTagsQ:
			existingTags.append(existingTag)
		return self.write(json.dumps(existingTags))


# To get the ID of an entity you just created: obj.key().id()

app = webapp2.WSGIApplication(
		[webapp2.Route("/home", handler=Home, name="index"),
		 webapp2.Route("/home/<page>", handler=Home, name="home"),
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


