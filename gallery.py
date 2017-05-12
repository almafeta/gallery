import hashlib
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
		name, passwd = web.input().name, web.input().passwd
		ident = db.select('example_users', where= 'name=$name', vars=locals())[0]
		try:
			if hashlib.sha512(dbsalt+passwd).hexdigest() == ident['pass']:
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
			form.Validator("Passwords must match", lambda i: i.password1 == i.password2)]
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
		namecheck = db.query("SELECT exists(SELECT 1 FROM gallery WHERE username=${un})", vars={'un':username})
		try:
			return namecheck[0]
		except:
			return render.register_error("An unknown error occurred.")

def loggedin():
	return (session.login==1)

app = web.application(urls, globals())
application = app.wsgifunc()
db = web.database(dbn='postgres', db='gallery', user='gallerydb', pw=secrets.dbpass)
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'login': 0})
