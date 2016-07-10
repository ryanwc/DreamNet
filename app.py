import os, webapp2, jinja2, re, hashlib, hmac, random, datetime, json
from datetime import date
import string, random, cPickle as pickle
from webapp2 import redirect_to
from google.appengine.ext import db

# third party lib
import bleach

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
	# what other properties?
	username = db.StringProperty(required = True)
	lc_username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	gender = db.StringProperty(required = True)
	birthdate = db.DateProperty(required = True)
	nationality = db.StringProperty(required = True)
	residence = db.StringProperty(required = True)
	area = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	profession = db.StringProperty(required = True)
	industry = db.StringProperty()
	sector = db.StringProperty()
	education_level = db.StringProperty(required = True)
	isParent = db.BooleanProperty(required = True)
	isCommitted = db.BooleanProperty(required = True)
	satisfaction_ratings = db.StringProperty(multiline = True, required = True)
	useful_dreams = db.StringProperty(required = True, multiline = True)

class Dream(db.Model):
	# what other properties?
	# do not need to record gender, nationality because those don't change
	# (if someone has a sex change, we'll just say they were always the new sex)
	user = db.ReferenceProperty(User,
							 	collection_name = "dreams")
	user_age = db.IntegerProperty(required = True)
	user_area = db.IntegerProperty(required = True)
	user_residence = db.IntegerProperty(required = True)
	user_education_level = db.StringProperty(required = True)
	user_profession = db.StringProperty(required = True)
	user_sector = db.StringProperty(required = True)
	user_industry = db.StringProperty(required = True)
	user_isParent = db.BooleanProperty(required = True)
	user_isCommitted = db.BooleanProperty(required = True)
	user_satsifaction_ratings = db.StringProperty(required = True, multiline = True)
	title = db.StringProperty(required = True)
	lc_title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	date_dreamt = db.DateProperty(required = True)
	date_posted = db.DateTimeProperty(auto_now_add=True)
	interruption = db.BooleanProperty(required = True)
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

# types, places, people, things, emotions, sensations
class TagGroup(db.Model):
	name = db.StringProperty(required = True)
	description = db.StringProperty()

class TagName(db.Model):
	name = db.StringProperty(required = True)
	lc_name = db.StringProperty(required = True)
	group = db.ReferenceProperty(TagGroup,
							     collection_name = "tag_names")
	description = db.StringProperty()

class Tag(db.Model):
	dream = db.ReferenceProperty(Dream,
								 collection_name = "tags")
	name = db.ReferenceProperty(TagName,
						    	collection_name = "tags")

# e.g., impossibility
class RealityCheckMechanism(db.Model):

	name = db.StringProperty(required = True)
	description = db.StringProperty(required = True)

# a specific user's unique dreamsigns
class DreamSign(db.Model):
	nickname = db.StringProperty(required = True)
	mechanism = db.ReferenceProperty(RealityCheckMechanism,
									 collection_name = "dream_signs")
	tag = db.ReferenceProperty(Tag,
							   collection_name = "dream_signs")
	user = db.ReferenceProperty(User,
								collection_name = "dream_signs")
	description = db.ReferenceProperty(required = True)

# specific instance of a reality check name, which could also be a dream sign
class RealityCheck(db.Model):
	tag = db.ReferenceProperty(Tag,
							   collection_name = "reality_checks")
	dream_sign = db.ReferenceProperty(DreamSign,
									  collection_name = "reality_checks")
	user = db.ReferenceProperty(User,
								collection_name = "reality_checks")
	dream = db.ReferenceProperty(Dream,
								 collection_name = "reality_checks")
	description = db.StringProperty()
	#success = db.BooleanProperty(required = True)
	# 0 = 1st RC in a specific dream, 3 = 4th, etc 
	#index = db.IntegerProperty(required = True)

### some globals

COUNTRIES = ["Afganistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antigua & Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bonaire", "Bosnia & Herzegovina", "Botswana", "Brazil", "British Indian Ocean Ter", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Canary Islands", "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Channel Islands", "Chile", "China", "Christmas Island", "Cocos Island", "Colombia", "Comoros", "Congo", "Cook Islands", "Costa Rica", "Cote DIvoire", "Croatia", "Cuba", "Curaco", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia", "French Southern Ter", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Great Britain", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guinea", "Guyana", "Haiti", "Hawaii", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea North", "Korea Sout", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malaysia", "Malawi", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Midway Islands", "Moldova", "Monaco", "Mongolia", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Nambia", "Nauru", "Nepal", "Netherland Antilles", "Netherlands", "Nevis", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Norway", "Oman", "Pakistan", "Palau Island", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Phillipines", "Pitcairn Island", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Montenegro", "Republic of Serbia", "Reunion", "Romania", "Russia", "Rwanda", "St Barthelemy", "St Eustatius", "St Helena", "St Kitts-Nevis", "St Lucia", "St Maarten", "St Pierre & Miquelon", "St Vincent & Grenadines", "Saipan", "Samoa", "Samoa American", "San Marino", "Sao Tome & Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "Spain", "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Tahiti", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks & Caicos Is", "Tuvalu", "Uganda", "Ukraine", "United Arab Erimates", "United Kingdom", "United States of America", "Uraguay", "Uzbekistan", "Vanuatu", "Vatican City State", "Venezuela", "Vietnam", "Virgin Islands (Brit)", "Virgin Islands (USA)", "Wake Island", "Wallis & Futana Is", "Yemen", "Zaire", "Zambia", "Zimbabwe"]
AREAS = ["Rural/Small Town", "Small/Medium City", "Large City"]

INDUSTRIES = ["Agriculture, Forestry, Fishing, and Hunting", "Automotive", "Arts, Entertainment, and Recreation", "Business Services - Administrative Support", "Business Services - Excluding Admin Support", "Construction", "Educational Services", "Finance/Banking", "Food Services and Drinking Establishments", "Health Services", "Hospitals", "Hospitality", "Insurance", "Manufacturing - Durable Goods", "Manufacturing - Nondurable Goods", "Museums/Historical Sites/Similar Institutions", "Natural Resources - Excluding Oil and Gas", "Natural Resources - Oil and Gas", "Other Information Services", "Postal Service", "Private Households", "Retail - Food and Beverage", "Retail - Household", "Retail - General", "Retail - Sporting, Hobby, or Leisure", "Scientific and Technical Services", "Publishing/Broadcasting - Excluding Internet", "Publishing/Broadcasting - Internet", "Real Estate", "Religious Institutions and Services", "Rental and Leasing Services", "Repair and Maintenance", "Social Assistance", "Telecommunications", "Transportation - Bulk Materials/Goods", "Transportation - Passengers", "Utilities", "Warehousing and Storage", "Waste Management and Remediation Services", "Wholesalers - Durable Goods", "Wholesalers - Nondurable Goods"]
SECTORS = ["Public", "Private", "Military"]
PROFESSIONS = ["Advertiser", "Accountant", "Actuary", "Administrative support professional", "Administrator", "Architect", "Artist", "Buying/purchasing professional", "Caretaker", "Clergy", "Corporate governance professional", "Corrections officer", "Designer", "Distribution/logistics professional", "Engineer", "Finance professional", "Human resources professional", "Information technology professional", "Judge", "Legislator", "Laborer", "Lawyer", "Lobbyist", "Manager", "Marketer", "Mathemetician", "Medical doctor", "Nurse", "Quality control professional", "Performer", "Politician", "Police officer", "Professor", "Psychologist / counseler", "Public relations professional", "Researcher", "Retired", "Salesperon", "Scientist", "Security professional", "Senior executive", "Skilled tradesperson", "Social worker", "Strategist", "Student", "Surveyor", "Teacher", "Translator", "Unemployed"]
NO_INDUSTRY_PROFESSIONS = ["Student", "Retired", "Unemployed"]
NO_SECTOR_PROFESSIONS = ["Retired", "Unemployed"]
EDUCATION_LEVELS = ["Have not graduated high school", "High school graduate or equivalent", "Trade school graduate", "College graduate", "Master's Degree", "Doctorate"]

SATISFACTION_AREAS = [{"name": "Career","code":"carsat"},{"name": "Finances","code":"finsat"}, {"name": "Mental Health","code":"mensat"}, {"name":"Physical Health","code":"physat"}, {"name":"Friends","code":"frisat"}, {"name":"Family","code":"famsat"}, {"name":"Significant Other / Romance","code":"romsat"}, {"name":"Personal Growth","code":"grosat"}, {"name":"Fun and Recreation","code":"funsat"}, {"name":"Physical Environment","code":"envsat"}]

GENDERS = ["Male", "Female", "Non-binary"]

# set mechanisms by which reality checks work
MECHANISMS = ["malfunction", "impossibility/oddity", "presence", "absence"]

# set some initial tags
TAGS = {}

TYPES = ["flying", "superhero-like", "falling", "nudity", "sexual", "nightmarish", "being chased",
		 "paralysis", "being trapped", "difficulty moving", "difficulty breathing", "eating", "death",
		 "violence", "testing/school exams", "aquatic", "demonic",
		 "religious", "angelic", "heavenly", "fantasy", "sci-fi", "romance", "comedy",
		 "being late", "missed appointment/event", "hellish",
		 "being in a hurry", "travel", "futuristic", "in the past", "light", "darkness",
		 "video game-like", "continuity error", "colorful", "black and white", "sepia",
		 "recurring", "magical", "extra ability", "illness", "medical", "floating",
		 "low gravity", "superpower", "driving", "peeing", "pooping"]

BEINGS = ["mother", "father", "brother", "sister", "cousin", "aunt", "uncle",
		  "son", "daughter", "neice", "nephew", "cousin", "grandfather",
    	  "grandmother", "grandson", "granddaughter", "mother-in-law",
		  "father-in-law", "brother-in-law", "sister-in-law", "son-in-law",
		  "daughter-in-law", "boss/manager", "direct report", "employee", 
		  "coworker", "wife", "girlfriend", "husband", "boyfriend", 
		  "best friend", "friend", "aquaintance", "business partner", "crush",
		  "person from childhood", "person from highschool", "lover",
		  "person from college", "teacher/professor", "specific fictional character",
		  "ghost", "caterpillar", "dog", "vampire", "angel", "demon", "spider",
		  "alien", "unicorn", "horse", "tiger", "lion", "bear", "God", "elf", "dwarf",
		  "orc", "wizard", "witch"]

PLACES = ["vaccuum/emptiness", "foreign country", "countryside", "kitchen",
		  "bedroom", "livingroom", "bathroom", "hallway", "ruins", "religious building",
		  "military base", "heaven", "hell", "beach", "house", "road/highway",
		  "ocean", "lake", "river", "swamp", "desert", "glacier", "rainforest",
		  "forest", "boat", "cave", "office building", "abandoned building",
		  "stadium", "open field", "farm", "mountain", "airport", "school",
		  "classroom", "hospital", "doctor's office", "science facility",
		  "outer space", "alien world", "Paris", "New York City", "Africa",
		  "USA", "France", "Germany", "Thailand", "Kuala Lumpur", "Bangkok", "Berlin",
		  "England", "London", "golf course"]

OBJECTS = ["bowl", "door", "hat", "chair",
		  "staircase", "flag", "gun", "knife", "car",
		  "boat", "airplane", "spoon", "fork", "table", "wall", "present",
		  "strawberry", "food", "blueberry", "analog timepiece", "digital timepiece", 
		  "light switch", "lightbulb", "mirror", "book", "door",
		  "window", "train", "elevator", "escalator", 
		  "bowl", "pants", "shirt", "dress", "skirt", 
		  "shoes", "cell phone", "laptop computer", "desktop computer", 
		  "tablet (computer)", "camera", "radio", "video player", "music player",
		  "spaceship", "teeth", "plate", "box", "can", "napkin", "video game console",
		  "physical video game", "banana", "hand", "face", "hair", "arm", "leg", "eye",
		  "ear", "nose", "mouth", "foot", "finger", "toe", "shoulder", "stomach"
		  "back", "wrist", "elbow", "knee", "ankle", "penis", "vagina", "testicle", 
		  "scalp", "skin", "neck", "butt", "calf", "hamstring", "bicep", "tricep",
		  "heel", "finger nail", "toenail", "scrotum", "bladder", "liver", "heart",
		  "brain", "gums", "tongue", "floss", "toothbrush", "toothpaste", "skull", "bone",
		  "gift", "money", "wallet", "chest", "breast", "spine", "glass"]

EMOTIONS = ["happiness", "ecstacy", "sadness", "sorrow/grief", "depression",
			"fear", "terror", "disgust", "anger", "indignation", "hatred",
			"love", "anxiety", "relief", "shame", "pride", "envy", "goodwill", 
			"confusion", "clarity", "stress", "relaxation", "caution", 
			"rashness", "kindness", "pity", "cruelty", "courage", "cowardice",
			"wonder", "boredom"]

SENSATIONS = ["pain", "discomfort", "pleasure", "orgasm", "taste", "color",
			  "red", "yellow", "green", "blue", "white", "black", "violet", 
			  "orange", "pink", "brown", "purple", "sour", "sweet", "salty",
			  "bitter", "umami", "comfort", "heat", "cold", "numbness",
			  "thirst", "hunger"]

TAGS['type'] = TYPES
TAGS['being'] = BEINGS
TAGS['place'] = PLACES
TAGS['object'] = OBJECTS
TAGS['emotion'] = EMOTIONS
TAGS['sensation'] = SENSATIONS


### helper functions

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (h, salt)

def correct_pw(name, pw, h):
	salt = h.split(",")[1]
	return h == make_pw_hash(name, pw, salt)

# set signin regexes and validators
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

SPECIAL_CHAR_RE = re.compile(r"[\!@\#\$%\^&\*]")
NUMBER_RE = re.compile(r"[0-9]")
LOWER_CASE_RE = re.compile(r"[a-z]")
UPPER_CASE_RE = re.compile(r"[A-Z]")
def valid_password(password):

	if len(password) < 6:
		print "short"
		return False

	if len(password) > 20:
		print "long"
		return False

	if not SPECIAL_CHAR_RE.search(password):
		print password
		print "spec"
		return False

	if not NUMBER_RE.search(password):
		print "num"
		return False

	if not LOWER_CASE_RE.search(password):
		print "up"
		return False

	if not UPPER_CASE_RE.search(password):
		print "low"
		return False

	return True

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
	return EMAIL_RE.match(email)

SECRET = 'examplesecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def is_passowrd(password):

	match

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

def get_valid_date(date):

	date_string = str(date)
	date_array = re.split(r"[^0-9]", date_string)

	year = int(date_array[0])
	month = int(date_array[1])
	day = int(date_array[2])

	# could throw ValueError exception
	return datetime.date(year, month, day)

# define template servers
class Home(Handler):
	def get(self, page=1):
		username = getUserFromSecureCookie(self.request.cookies.get("username"))

		'''
		# only do first time
		for group in TAGS:
			group = TagGroup(name=group)
			group.put()
			for tagname in TAGS[group.name]:
				tag = TagName(name=tagname, lc_name=tagname.lower(), group=group)
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

		user = User.all().filter("username =", username).get();

		userDreamsigns = []

		for dreamsign in user.dream_signs:
			userDreamsigns.append(dreamsign.nickname)

		tagsQ = TagName.all()
		tagsQ.order("lc_name")
		groupsQ = TagGroup.all()
		tagGroupToNames = {}
		tagNameToGroup = {}
		objectTags = []
		nonObjectTags = []

		for tagGroup in groupsQ:
			tagGroupToNames[tagGroup.name] = []

		for tag in tagsQ:
			print tag.name
			tagNameToGroup[tag.name] = tag.group.name
			tagGroupToNames[tag.group.name].append(tag.name)

		self.render("newdream.html", dreamDict=None, 
					messages=None, tagGroupToNames=json.dumps(tagGroupToNames),
					tagNameToGroup=json.dumps(tagNameToGroup), realityChecks=tagGroupToNames,
					userDreamsigns=userDreamsigns)

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

		dreamDict["date_dreamt"] = bleach.clean(self.request.get("datedreamt"))
		## change for international versions?
		if dreamDict["date_dreamt"]:

			date_dreamt = None

			try:
				date_dreamt = get_valid_date(dreamDict["date_dreamt"])
			except ValueError:
				messages["date_dreamt"] = {"message": "Please fix the date formatting (mm/dd/yyyy)",
							 	 	       "validity": "invalid"}

			if date_dreamt:
				dreamDict["date_dreamt"] = date_dreamt

				if dreamDict["date_dreamt"] > datetime.datetime.now():
					messages["date_dreamt"] = {"message": "Date dreamt cannot be in the future",
								 	 	       "validity": "invalid"}
				else:
					messages["date_dreamt"] = {"message": "Date dreamt OK",
				 	 	     "validity": "valid"}
		else:
			messages["date_dreamt"] = {"message": "Please provide the day you had the dream",
							 	 	   "validity": "invalid"}		

		dreamDict["date_posted"] = datetime.datetime.now()
		messages["date_posted"] = {"message": "Date posted OK",
						    	   "validity": "valid"}

		dreamDict["lucidity"] = bleach.clean(self.request.get("lucidity"))
		if dreamDict["lucidity"]:
			
			if (dreamDict["lucidity"] != "True" and 
				dreamDict["lucidity"] != "False"):

				messages["lucidity"] = {"message": "Answer 'Yes' or 'No'",
							 	 	    "validity": "invalid"}
			else:
				messages["lucidity"] = {"message": "Lucidity answer OK",
							 	 	    "validity": "valid"}	

			if dreamDict["lucidity"] == "True":

				dreamDict["lucid_reason"] = bleach.clean(self.request.get("lucidreason"))

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

						dreamDict["something_else"] = bleach.clean(self.request.get("somethingelse"))

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

				dreamDict["lucid_length"] = bleach.clean(self.request.get("lucidlength"))

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

		dreamDict["control"] = bleach.clean(self.request.get("control"))
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

		dreamDict["enjoyability"] = bleach.clean(self.request.get("enjoyability"))
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
		
		dreamDict["title"] = bleach.clean(self.request.get("title"))
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

		dreamDict["description"] = bleach.clean(self.request.get("description"))
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

		inputTags = bleach.clean(self.request.get("dreamtags"))
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

		dreamDict["content"] = bleach.clean(self.request.get("content"))
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
		tagsQ.order("lc_name")
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

					userDreamsigns = []

					for dreamsign in user.dream_signs:
						userDreamsigns.append(dreamsign.nickname)

					return self.render("newdream.html", dreamDict=dreamDict, 
						messages=messages, tagGroupToNames=json.dumps(tagGroupToNames),
						tagNameToGroup=json.dumps(tagNameToGroup),
						userDreamsigns=userDreamsigns)

		# set values for datastore (some cannot be string)
		if dreamDict["lucidity"] == "True":
			dreamDict["lucidity"] = True
		else:
			dreamDict["lucidity"] = False

		dreamDict["control"] = int(dreamDict["control"])
		dreamDict["enjoyability"] = int(dreamDict["enjoyability"])

		# set the "point in time" user variables for this dream
		dreamDict["user_age"] = datetime.date.today().year - user.birthdate.year
		dreamDict["user_area"] = user.area
		dreamDict["user_residence"] = user.residence
		dreamDict["user_education_level"] = user.education_level
		dreamDict["user_profession"] = user.profession
		dreamDict["user_sector"] = user.sector
		dreamDict["user_industry"] = user.industry
		dreamDict["user_isParent"] = user.isParent
		dreamDict["user_isCommitted"] = user.isCommitted
		dreamDict["user_satsifaction_ratings"] = user.satisfaction_ratings

		dreamDict["lc_title"] = dreamDict["title"].lower()

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
				tagNameObj = TagName(name=tag_name, lc_name=tag_name.lower(), group=tagGroupObj)
				tagNameObj.put()
			else:
				tagNameObj = existingTagName

			dreamTag = Tag(dream=dream, name=tagNameObj)

		return redirect_to("viewdream", id=str(dream.key().id()))

class Register(Handler):
	def get(self):

		sorted(COUNTRIES, key=lambda s: s.lower())
		sorted(INDUSTRIES, key=lambda s: s.lower())
		sorted(PROFESSIONS, key=lambda s: s.lower())
		sorted(EDUCATION_LEVELS, key=lambda s: s.lower())
		sorted(SECTORS, key=lambda s: s.lower())

		self.render("register.html", countries=COUNTRIES, industries=INDUSTRIES,
			professions=PROFESSIONS, educationLevels=EDUCATION_LEVELS, sectors=SECTORS,
			satisfactionAreas=SATISFACTION_AREAS, satisfactionRatings=None,
			values=None, messages=None)

	def post(self):

		# use userDict to pass values to User constructor or to form if an input is not valid
		values = {}

		values['username'] = bleach.clean(self.request.get("username"))
		values['password'] = bleach.clean(self.request.get("password"))
		values['verify_password'] = bleach.clean(self.request.get("verifypassword"))
		values['email'] = bleach.clean(self.request.get("email"))
		values['birthdate'] = bleach.clean(self.request.get("birthdate"))
		values['gender'] = bleach.clean(self.request.get("gender"))
		values['nationality'] = bleach.clean(self.request.get("nationality"))
		values['residence'] = bleach.clean(self.request.get("residence"))
		values['area'] = bleach.clean(self.request.get("area"))
		values['profession'] = bleach.clean(self.request.get("profession"))
		values['education_level'] = bleach.clean(self.request.get("educationlevel"))
		values['isCommitted'] = bleach.clean(self.request.get("iscommitted"))
		values['isParent'] = bleach.clean(self.request.get("isparent"))

		# holds message for user about input and 
		# whether input is valid or invalid
		messages = {}
		hasInvalid = False

		### CLEAN INPUT WITH BLEACH OR SIMILAR IF PRODUCTION

		satisfactionRatings = {}
		for SATISFACTION_AREA in SATISFACTION_AREAS:

			thisAreaRating = bleach.clean(self.request.get(SATISFACTION_AREA['code']))

			if thisAreaRating:

				try:

					thisAreaRating = int(thisAreaRating)

					if (thisAreaRating < 0 or
						thisAreaRating > 10):

						messages[SATISFACTION_AREA['code']] = {"message": SATISFACTION_AREA['name'] + " invalid.",
								 		 	          "validity": "invalid"}
						hasInvalid = True
					else:
						messages[SATISFACTION_AREA['code']] = {"message": SATISFACTION_AREA['name'] + " valid",
								 		 	          "validity": "valid"}
				except ValueError:

					messages[satisfactionArea['code']] = {"message": SATISFACTION_AREA['name'] + " invalid.",
								 	 	          "validity": "invalid"}	
					hasInvalid = True	
			else:
				messages[satisfactionArea['code']] = {"message": "Please provide a satisfaction level for " + SATISFACTION_AREA['name'],
											  "validity": "invalid"}
				hasInvalid = True

			satisfactionRatings[SATISFACTION_AREA['code']] = thisAreaRating

		# name must be only alphabetic chars
		if values['username']:
			if valid_username(values['username']):
				messages["username"] = {"message": "Name OK",
							 		"validity": "valid"}
			else:
				messages["username"] = {"message": "Name invalid",
									"validity": "invalid"}	
				hasInvalid = True		
		else:
			messages["username"] = {"message": "Please provide a name",
								"validity": "invalid"}
			hasInvalid = True

		# not the "best" password but could improve for production
		if values['password']:
			if valid_password(values['password']):
				messages["password"] = {"message": "Password OK",
						 				"validity": "valid"}
			else:
				messages["password"] = {"message": "Password invalid",
						 				"validity": "invalid"}
				hasInvalid = True	
		else:
			messages["password"] = {"message": "Please provide a pasword",
								    "validity": "invalid"}
			hasInvalid = True

		# verifypassword must match password
		if values['verify_password']:
			if not values['verify_password'] == values['password']:
				messages["verify_password"] = \
					{"message": "Verify password does not match password",
		 			 "validity": "invalid"}
				hasInvalid = True
		 	else:
				messages["verify_password"] = {"message": "OK (password "+\
							"matches)", "validity": "valid"}
		else:
			messages["verify_password"] = {"message": "Please verify password",
								    	  "validity": "invalid"}
			hasInvalid = True

		# email must be valid email
		if values['email']:
			if valid_email(values['email']):
				messages["email"] = {"message": "Email is valid",
									 "validity": "valid"}
			else:
				messages["email"] = {"message": "Email is invalid",
									 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["email"] = {"message": "Please provide an email",
								 "validity": "invalid"}
			hasInvalid = True

		if values['birthdate']:

			birthdate = None

			try:
				birthdate = get_valid_date(values['birthdate'])
			except ValueError:
				messages["birthdate"] = {"message": "Please fix the date formatting (mm/dd/yyyy)",
							 	 	       "validity": "invalid"}
				hasInvalid = True

			if birthdate:
				values["birthdate"] = birthdate

				if values["birthdate"] > datetime.date.today():
					messages["birthdate"] = {"message": "Birthdate cannot be in the future",
								 	 	       "validity": "invalid"}
					hasInvalid = True
				else:
					messages["birthdate"] = {"message": "Birthdate OK",
				 	 	     "validity": "valid"}
		else:
			messages["birthdate"] = {"message": "Please provide a birthdate",
								 "validity": "invalid"}
			hasInvalid = True

		if values['gender']:
			if values['gender'] in GENDERS:
				messages["gender"] = {"message": "Gender OK",
									 	 "validity": "valid"}
			else:
				messages["gender"] = {"message": "Gender is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["gender"] = {"message": "Please provide a gender",
								 "validity": "invalid"}
			hasInvalid = True

		if values['nationality']:
			if values['nationality'] in COUNTRIES:
				messages["nationality"] = {"message": "Nationality OK",
									 	 "validity": "valid"}
			else:
				messages["nationality"] = {"message": "Nationality is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["nationality"] = {"message": "Please provide a nationality",
								 "validity": "invalid"}	
			hasInvalid = True

		if values['residence']:
			if values['residence'] in COUNTRIES:
				messages["residence"] = {"message": "Residence OK",
									 	 "validity": "valid"}
			else:
				messages["residence"] = {"message": "Residence is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["residence"] = {"message": "Please provide a current country of residence",
								 "validity": "invalid"}	
			hasInvalid = True

		if values['area']:
			if values['area'] in AREAS:
				messages["area"] = {"message": "Area OK",
									 	 "validity": "valid"}
			else:
				messages["area"] = {"message": "Area is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["area"] = {"message": "Please pick the option that best describes where you live",
								 "validity": "invalid"}	
			hasInvalid = True

		if values['education_level']:
			if values['education_level'] in EDUCATION_LEVELS:
				messages["education_level"] = {"message": "Education level OK",
									 	 "validity": "valid"}
			else:
				messages["education_level"] = {"message": "Education is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["education_level"] = {"message": "Please provide an education level",
								 "validity": "invalid"}
			hasInvalid = True

		if values['profession']:
			if values['profession'] in PROFESSIONS:
				messages["profession"] = {"message": "Profession OK",
									 	 "validity": "valid"}

				if values['profession'] not in NO_INDUSTRY_PROFESSIONS:

					values['industry'] = bleach.clean(self.request.get("industry"))

					if values['industry']:
						if values['industry'] in INDUSTRIES:
							messages["industry"] = {"message": "Industry OK",
												 	 "validity": "valid"}
						else:
							messages["industry"] = {"message": "Industry is invalid",
												 	 "validity": "invalid"}
							hasInvalid = True
					else:
						messages["industry"] = {"message": "Please provide an industry",
											 "validity": "invalid"}	
						hasInvalid = True
				else:
					values['industry'] = None

				if values['profession'] not in NO_SECTOR_PROFESSIONS:

					values['sector'] = bleach.clean(self.request.get("sector"))

					if values['sector']:
						if values['sector'] in SECTORS:
							messages["sector"] = {"message": "Sector OK",
												 	 "validity": "valid"}
						else:
							messages["sector"] = {"message": "Sector is invalid",
												 	 "validity": "invalid"}
							hasInvalid = True
					else:
						messages["sector"] = {"message": "Please provide a sector",
											 "validity": "invalid"}	
						hasInvalid = True
				else:
					values['sector'] = None
			else:
				messages["profession"] = {"message": "Profession is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["profession"] = {"message": "Please provide a profession",
								 "validity": "invalid"}
			hasInvalid = True

		if values['isParent']:
			if (values['isParent'] == "True" or
				values['isParent'] == "False"):
				messages["isParent"] = {"message": "Parent status OK",
									 	"validity": "valid"}

				if values['isParent'] == "True":
					values["isParent"] = True
				else:
					values["isParent"] = False
			else:
				messages["isParent"] = {"message": "Parent status is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["isParent"] = {"message": "Please indicate whether you are a parent",
								 "validity": "invalid"}
			hasInvalid = True

		if values['isCommitted']:
			if (values['isCommitted'] == "True" or
				values['isCommitted'] == "False"):
				messages["isCommitted"] = {"message": "Committed status OK",
									 	"validity": "valid"}

				if values['isCommitted'] == "True":
					values["isCommitted"] = True
				else:
					values["isCommitted"] = False
			else:
				messages["isCommitted"] = {"message": "Committed status is invalid",
									 	 "validity": "invalid"}
				hasInvalid = True
		else:
			messages["isCommitted"] = {"message": "Please indicate whether you are in a committed relationship",
								 "validity": "invalid"}
			hasInvalid = True

		saltedpasshash = make_pw_hash(values['username'], values['password'])

		# if any field was invalid, re-render the form while saving all input
		# and giving a valid/invalid message for each input 
		# could make more efficient by flagging boolean "hasInvalid" previously
		if hasInvalid:

			sorted(COUNTRIES, key=lambda s: s.lower())
			sorted(INDUSTRIES, key=lambda s: s.lower())
			sorted(PROFESSIONS, key=lambda s: s.lower())
			sorted(EDUCATION_LEVELS, key=lambda s: s.lower())
			sorted(SECTORS, key=lambda s: s.lower())

			# these are booleans right now.  str needed?
			values['isCommitted'] = str(values['isCommitted'])
			values['isParent'] = str(values['isParent'])

			print values['nationality']
			return self.render("register.html", values=values, 
				messages=messages, countries=COUNTRIES, industries=INDUSTRIES,
				professions=PROFESSIONS, educationLevels=EDUCATION_LEVELS, 
				sectors=SECTORS, satisfactionAreas=SATISFACTION_AREAS,
				satisfactionRatings=satisfactionRatings)

		# prepare arguments for User constructor
		userDict = values
		userDict.pop("verifypassword", None)
		useful_dreams = {}
		userDict["password"] = saltedpasshash
		userDict["useful_dreams"] = pickle.dumps(useful_dreams)
		userDict["satisfaction_ratings"] = pickle.dumps(satisfactionRatings)

		userDict["lc_username"] = userDict["username"].lower()

		user = User(**userDict)
		user.put()

		# if more than one with this email or user name, delete this one
		# and return invalid. hacky workaround of seemingly bad google 
		# datastore support for unique entity values (username and email should be unique)
		# if we tested before while verifying name, then when we get to point of User creation
		# someone else could have used the name.  this way, that is not possible
		duplicate = False

		users = User.all()
		users.filter("username =", user.username)
		numSameUsername = 0
		for u in users.run():
			numSameUsername += 1
			if numSameUsername > 1:
				messages["username"] = {"message": "Name already taken",
									"validity": "invalid"}
				user.delete()
				duplicate = True
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
				duplicate = True
				break

		if duplicate:

			sorted(COUNTRIES, key=lambda s: s.lower())
			sorted(INDUSTRIES, key=lambda s: s.lower())
			sorted(PROFESSIONS, key=lambda s: s.lower())
			sorted(EDUCATION_LEVELS, key=lambda s: s.lower())
			sorted(SECTORS, key=lambda s: s.lower())

			# these are booleans right now.  str needed?
			values['isCommitted'] = str(values['isCommitted'])
			values['isParent'] = str(values['isParent'])

			return self.render("register.html", values=values, 
				messages=messages, countries=COUNTRIES, industries=INDUSTRIES,
				professions=PROFESSIONS, educationLevels=EDUCATION_LEVELS, 
				sectors=SECTORS, satisfactionAreas=SATISFACTION_AREAS,
				satisfactionRatings=satisfactionRatings)

		username_cookie_val = make_secure_val(user.username)

		response = redirect_to("home", page=1)
		response.set_cookie("username", username_cookie_val)
		return response

class Signin(Handler):
	def get(self):

		self.render("signin.html", values=None, messages=None)

	def post(self):

		name = bleach.clean(self.request.get("name"))
		password = bleach.clean(self.request.get("password"))

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
					if correct_pw(user.username, password, saltedpasshash):
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


