import os, webapp2, jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
	autoescape=True, auto_reload=True)


# set the dictionaries for converting alphabetic chars to ints and vice versa
alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
			"l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
			"w", "x", "y", "z"]

numToAlpha = {}
alphaToNum = {}

for x in range(0, 26):
	numToAlpha[x] = alphabet[x]
	alphaToNum[alphabet[x]] = x

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):

		self.render("index.html")

	def post(self):

		inputText = self.request.get("text")
		rot13Text = ""

		for char in inputText:
			if char.isalpha():
				position = alphaToNum[char.lower()]
				newPosition = position + 13
				if newPosition > 25:
					newPosition = newPosition - 25 - 1
				newChar = numToAlpha[newPosition]
				if char.isupper():
					newChar = newChar.upper()
				rot13Text += newChar
			else:
				rot13Text += char

		self.render("index.html", rot13Text=rot13Text)

app = webapp2.WSGIApplication([('/', MainPage)],
							  debug=True)
