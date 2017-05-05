import web

urls = (
	'/', 'index'
)

app = web.application(urls, globals())

class index:
	def GET(self):
		return "<html><head><title>Gallery Install Successful</title></head><body><p>Heya!</p><p>If you're seeing this, setup.sh worked and your box is all set to go.</p><p>Of course, there's still plenty to do.  Check <a href=https://github.com/almafeta/gallery>the Github repository</a>, particularly <a href=https://github.com/almafeta/gallery/issues>issues</a>, for things to do from here.</p><p>- Shanya</p></body></html>"

application = app.wsgifunc()
