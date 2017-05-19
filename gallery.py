import passlib
import secrets
import web
from web import form

urls = (
	'/', 'index',
	'/login', 'login',
	'/logout', 'logout',
	'/register', 'register'
)

class index:
	def GET(self):
		if session.login == 1 and isnewuser(session.userid):
			return render.newuser()

		return render.index()

class login:
	def GET(self):
		if session.login == 1:
			return render.index()
		else:
			return render.login()

	def POST(self):
		from passlib.context import CryptContext
		password_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

		if session.login == 1:
			return render.index()

		i = web.input()
		username = i.user
		ident = db.select('gallery.users', where='username=$username', vars=locals())[0]
		try:
			if password_context.verify(i.passwd, ident['password']):
				session.login = 1
				session.userid = ident['id']
				session.admin = ident['admin']
				return render.login()
				#return render.login_ok()
			else:
				session.login = 0
				session.admin = 0
				session.userid = 0
				return render.login()
				#return render.login_error()
		except:
			session.login=0
			session.admin=0
			session.userid=0
			return render.login()
			#return render.login_error()

class logout:
	def GET(self):
		session.kill()
		return render.index()

class register:
	registration_form = form.Form(
		form.Textbox("username", description="Login"),
		form.Password("password1", description="Password"),
		form.Password("password2", description="Repeat password"),
		form.Button("submit", type="submit", description="Register!"),
		validators = [
			form.Validator("Passwords must match!", lambda i: i.password1 == i.password2),
			form.Validator("Password is too short!", lambda i: len(i.password1) <= 9)]
	)

	def GET(self):
		f = register.registration_form()
		return render.register(f)

	def POST(self):
		f = register.registration_form()
		if not f.validates():
			return render.register(f)

		i = web.input()
		username, passwd = i.username, i.password1

		try:
			namecheck = db.query("SELECT exists(SELECT 1 FROM gallery.users WHERE username=${un})", vars={'un':username})
		except Exception as e:
			return "Unhandled database exception."

		if namecheck[0]['exists']:
			return "<p>This username is already available.</p>"
		else:
			self.createuser(i.username, i.password1)
			return "<p>Created user!  Try to <a href=/login>log in</a>.</p>"

	def createuser(self, username, password):
		from passlib.context import CryptContext
		password_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

		cryptedpassword = password_context.hash(password)
		db.insert('gallery.users', admin=False, password=cryptedpassword, username=username)

		createduser = db.select('gallery.users', where="username=${un}", vars={'un':username})
		db.insert('gallery.userflags', userid=createduser[0]['id'], flagtype="newuser")

def loggedin():
	return (session.login==1)

def isnewuser(userid):
	if userid == 0:
		return false;

	newuser = db.query("SELECT exists(SELECT 1 FROM gallery.userflags WHERE userid=${uid} AND flagtype=\"newuser\")", vars={'uid':str(userid)})
	return newuser[0]['exists']

app = web.application(urls, globals())
application = app.wsgifunc()
db = web.database(dbn='postgres', db='gallery', user='gallerydb', pw=secrets.dbpass)
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'login': 0, 'userid': 0})
render = web.template.render('templates', base='layout', globals={'session': session})
