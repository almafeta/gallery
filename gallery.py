
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
		render = web.template.render('templates', base='layout')
		return render.index()

class login:
	def GET(self):
		render = web.template.render('templates', base='layout')
		return render.login()

	def POST(self):
		from passlib.context import CryptContext
		password_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

		name, passwd = web.input().name, web.input().passwd
		ident = db.select('example_users', where='username=$name', vars=locals())[0]
		try:
			if password_context.verify(password, ident['password']):
				session.login = 1
				session.admin = ident['admin']
				return render.login()
				#return render.login_ok()
			else:
				session.login = 0
				session.admin = 0
				return render.login()
				#return render.login_error()
		except:
			session.login=0
			session.admin=0
			return render.login()
			#return render.login_error()

class logout:
	def GET(self):
		render = web.template.render('templates', base='layout')
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
		render = web.template.render('templates', base='layout')
		return render.register(f)

	def POST(self):
		f = register.registration_form()
		render = web.template.render('templates', base='layout')
		if not f.validates():
			return render.register(f)

		i = web.input()
		username, passwd = i.username, i.password1

		try:
			namecheck = db.query("SELECT exists(SELECT 1 FROM gallery.users WHERE username=${un})", vars={'un':username})
		except Exception as e:
			return "Unhandled exception."

		if namecheck[0]['exists']:
			return "<p>True!</p>"
		else:
			createuser(i.username, i.password1)
			return "<p>Created user!  Try to <a href=/login>log in</a>.</p>"

	def createuser(username, password):
		from passlib.context import CryptContext
		password_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

		cryptedpassword = password_context.hash(password)
		db.insert(admin=False, password=cryptedpassword, username=username)

def loggedin():
	return (session.login==1)

app = web.application(urls, globals())
application = app.wsgifunc()
db = web.database(dbn='postgres', db='gallery', user='gallerydb', pw=secrets.dbpass)
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'login': 0})
