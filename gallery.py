import hashlib
import secrets
import web

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
	def GET(self):
		render = web.template.render('templates', base='layout')
		return render.register()

def loggedin():
	return (session.login==1)

app = web.application(urls, globals())
application = app.wsgifunc()
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'login': 0})
