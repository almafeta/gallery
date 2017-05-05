def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	return ["<p>Heya!</p><p>If you're seeing this, setup.sh worked and your box is all set to go.</p><p>Of course, there's still plenty to do.  Check <a href=https://github.com/almafeta/gallery>the Github repository</a>, particularly <a href=https://github.com/almafeta/gallery/issues>issues</a>, for things to do from here.</p><p>- Shanya</p>"]
