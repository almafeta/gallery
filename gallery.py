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
		return render.index()

class logout:
	def GET(self):
		render = web.template.render('templates', base='layout')
		return render.index()

class register:
	def GET(self):
		render = web.template.render('templates', base='layout')
		return render.register()

app = web.application(urls, globals())
application = app.wsgifunc()
