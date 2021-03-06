#!/usr/bin/env python
# encoding: utf-8
"""
agenda_fest_api.py

AJAXy cherrypy, merging lots of fun

"""
import cherrypy
import webbrowser
import os
import simplejson
import sys
import urllib
import urllib2
import math

import pylast

from likeThis import *
from artist import *
from schedulepicker import *
from sonar_times import *
from credentials import *

MEDIA_DIR = os.path.join(os.path.abspath("."), u"media")

fest2uuid = {'greenman' : '21c7356b82b04771966b08c122543064',
	     'womad' : '673139f25d684e718709ea51299ccf05',
      	     'downloadfestival' : '8020e8c93a5d4c19a913e253c44f2e8f',
	     'bestival' : '97aa4ce95e92412ca914300526a3cc99',
	     'sonar' : 'a374b1e3bbfa4107890b56ed74c7e7fe',
	     'glastonbury' : 'b16a75d1be374a0485da7f987deb841f',
	     'hopfarm' : 'e2456c5842294759a54d3c9409af0755',
	     'fleadh' : 'f1b0e90e837d4144ac9760efd7024b08',
	     'leedsreading' : 'f6fbc6cacccc44acbe495aede3aad112',
	     'standoncalling' : 'fecca33180824101a75d6cbc30e772ff',
	     'wacken' : 'b185c91728844e738d45d13765b94993'}


class AgendafestApi(object):
				
	@cherrypy.expose
	def index(self):
		return open(os.path.join(MEDIA_DIR, u'index.html'))

	@cherrypy.expose
	def getlfmartists(self, username):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		out = lfm_artists(username)
		if len(out['top_artists']) == 0:
			out =  lfm_artists(username, period = 'overall')
		out['response'] = 'ok'
		return simplejson.dumps(out)

	@cherrypy.expose
	def festlist(self, festname):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return simplejson.dumps(festy(festname))

	@cherrypy.expose
	def intersect(self, username, festname):
		cherrypy.response.headers['Content-Type'] = 'applications/json'
		return simplejson.dumps({'response':'ok',
								'result':merge(username, festname)})

	# non AJAX workflow here:
	@cherrypy.expose
	def agenda(self):
		return"""<!DOCTYPE html PUBLIC
                        "-//W3C//DTD XHTML 1.0 Transitional//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
                <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
                <head>
                </head>
                <body class="inbook">
                       <div id="backTextureInner" style="height:360px;">
                             <div class="dialogue"> 
                                  We only support last.fm history based personalisation currently...
                                  <a href="/media/festivals.html"><span class="createAgenda">Start Again...</span></a>
                             </div>
                       </div>
                 </body>
                      """
	@cherrypy.expose
	def fest(self, festival=None):
		cherrypy.response.headers['Content-Type'] = 'text/html'
		return """<!DOCTYPE html PUBLIC
			"-//W3C//DTD XHTML 1.0 Transitional//EN"
			"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"> 
		<head> 
			<meta http-equiv="content-type" content="text/html; charset=UTF-8" /> 

			<title>AGENDAFEST</title> 
			<meta name = "viewport" content = "width = device-width">
			<meta name="Author"			content="" /> 
			<meta name="publisher"		content="" /> 
			<meta name="copyright"		content="" /> 
			<meta name="description"	content="" /> 
			<meta name="keywords"		content="" /> 

			<link rel="shortcut icon" href="" /> 

			<link rel="stylesheet" type="text/css" href="media/style.css" /> 


		</head>

		<body class="inbook">

			<div id="backTextureInner" style="height:400px;">

				<div class="dialogue">
					Builds your perfect festival agenda by matching your music tastes with recommended artists...
				</div>	
				<form id="agenda" action="buildagenda" method='get'>
				<input type="hidden" name="festival" value="{festname}" />
				<input class="simple" name="username" onfocus="this.value=''" value="Enter Last.fm username" /> 

				
<span class="lastfmBtn"><input type="submit" id="thebutton" class="createAgenda" value="Who should I see?"/>
					</span></a>
				</form>
                                


				<div class="dialogue2">Don't have an account?	<br><span style="color:#666;">+ Add you favourite Artists...</span> </div>	


					<input class="simple" onfocus="this.value=''" style="margin-bottom:-14px;" value="Enter artist name" />
					<span class="explanationInput">e.g Radiohead, Sufjan Stevens, Sparklehorse...</span>


				<div class="tasteFooter">
					<a href="agenda"><span class="createAgenda">Build my Agenda</span></a>

				</div>


			</div>


		</body>

		</html>""".format(festname = festival)

	@cherrypy.expose
	def buildagenda(self, festival=None, username=None, cal = None, x=None, y=None):
		cherrypy.response.headers['Content-Type'] = 'text/html'
		cherrypy.session['festival']=festival
		if cal and festival in ['sonar']:
			sp = schedulepicker(merge(username, festival, retDict = True), sonar)
			sp.build_cal()
			schedule = sp.agenda
			"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
			   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
			<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
			<head>
			<title>Agendafest - Festivals on auto-pilot</title>
			<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
			</head>
			<body class="inbook" style="width: 600px;margin:auto">
			<h1 id="title">{last_name}'s {festname}</h1>
			<h3 id="subtitle">Top recommends:</h3>
			<ul>
				{listOfFun}
			</ul>
			</body>
			</html>		
			""".format(festname = festival.title(), last_name = username,
						listOfFun = reduce(lambda x,y:x+y, map(lambda performance: \
							'\t\t\t<li>See <b><a href="getinfo?artist={0}&time={1}&date={2}&stage={3}">{5}</a></b> because you like {1}, Score: {4}</li>\n'.format(urllib.quote(performance[3].encode('utf8')), performance[1].encode('utf8'), performance[0], performance[2], performance[4], performance[3].encode('utf8')), schedule)))
		else:
			return """	<!DOCTYPE html PUBLIC
													"-//W3C//DTD XHTML 1.0 Transitional//EN"
													"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
												<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"> 
												<head> 
													<meta http-equiv="content-type" content="text/html; charset=UTF-8" /> 

													<title>AGENDAFEST</title> 
													<meta name = "viewport" content = "width = device-width">
													<meta name="Author"			content="" /> 
													<meta name="publisher"		content="" /> 
													<meta name="copyright"		content="" /> 
													<meta name="description"	content="" /> 
													<meta name="keywords"		content="" /> 

													<link rel="shortcut icon" href="" /> 

													<link rel="stylesheet" type="text/css" href="media/style.css" /> 


												</head>

												<body class="inbook">

													<div id="backTextureInner">


														<div id="header" class="gothic">

															<a href="media/festivals.html"><span class="backtoFest">Festivals</span></a>
															<span class="titleCentered"><span style="color:#666">MY</span> {festname}</span>
														</div>

														<div id="subBar">

															<div id="day">Friday 17th of June</div>
															<div class="shuffle"></div>

														</div>


														<ul class="list agenda">

															</a>
												
															{listOfFun}

														</ul>

													</div>
to

												</body>

												</html>""".format(festname = festival.upper(), last_name = username,
															listOfFun = reduce(lambda x,y:x+y, map(lambda performance: \
														'\t\t\t<a href="getinfo?artist={1}&stage={4}&username={2}"><li><span class="gothic time">n&#176; {0}</span>\n<span class="item">{3}</span>\n<span class="listarrow"></span>\n</li>\n</a>'.format(performance[0]+1, urllib.quote(performance[1][0].encode('utf8')), username, performance[1][0].encode('utf8'),festival.title()),enumerate(merge(username, festival)))))
	@cherrypy.expose
	def getinfo(self, artist=None, time="----", date="", stage="", username=None):
		cherrypy.response.headers['Content-Type'] = 'text/html'
		artist_description, genre, url_list = get_description(artist)
		image_url = get_image(artist)
		audio = get_preview(artist)
		print "audio link", audio
		if image_url:
			image_block = "<img src={0} />".format(image_url)
		else:
			image_block = '<span style="height:126px;width=126px>No Picture</span>'
		if len(url_list) > 0:
			moreinfo_block = "<ul>More Info:\n"
			for outlink in url_list:
				moreinfo_block += '\t<li><a href="{link}">{source}</a></li>\n'.format(link=outlink[1], source=outlink[0])
			moreinfo_block += "</ul>"
		else:
			moreinfo_block = ""
		try:
			why_string = "<span class=\"relation\">Go see them because you also like</span><span id=\"relatedArtist\"> {artist}, </span><span class=\"relation\">as they both feature a bit of</span><span id=\"relatedArtist\"> {tag}</span>".format(artist=cherrypy.session.get(artist)[0][1], tag=cherrypy.session.get(artist)[1])
		except KeyError:
			print artist, "not in cookie session"
			why_string = "<span class=\"relation\"></span>"
		except:
			print 'weirdness trying to sort provenance of rec for', artist
			why_string = "<span class=\"relation\"></span>"
		try:
			fest=cherrypy.session.get('festival')
		except:
			fest=None
		
		return """			<!DOCTYPE html PUBLIC
						"-//W3C//DTD XHTML 1.0 Transitional//EN"
						"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
					<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"> 
					<head> 
						<meta http-equiv="content-type" content="text/html; charset=UTF-8" /> 

						<title>AGENDAFEST</title> 
						<meta name = "viewport" content = "width = device-width">
						<meta name="Author"			content="" /> 
						<meta name="publisher"		content="" /> 
						<meta name="copyright"		content="" /> 
						<meta name="description"	content="" /> 
						<meta name="keywords"		content="" /> 

						<link rel="shortcut icon" href="" /> 

						<link rel="stylesheet" type="text/css" href="media/style.css" /> 


					</head>

					<body class="inbook">

						<div id="backTextureInner">


							<div id="header">

								<a href="buildagenda?festival={festname}&username={username}"><span class="backtoAgenda">Agenda</span></a>

								<span class="swapArtist">Shuffle this slot</span>
							</div>

							<div id="artistImage">
								<a href="{audio_url}">
								{image_block}
								<span id="play"></span></a>
							</div>
							<div id="artistInfo">
								<span id="timeDetail">{time}</span>
								<span id="ArtistName"> {artistName}</span>
								<span id="details">{date} / {stage} </span>
                                                                {provenance}

							</div>

							<div id="description">
								{description}
							</div>

							<div id="links">
							{moreinfo}
							</div>

						</div>


					</body>

					</html>""".format(artistName=artist,image_block=image_block, audio_url=audio, time=time[:-2]+':'+time[-2:],date = date, 
								stage=stage, genre = genre, description = artist_description, moreinfo=moreinfo_block, username=username, provenance=why_string, festname=fest)
		
config = {'global':
                                {'server.socket_host': '127.0.0.1',
                                 'enviroment':'production',
                                 'log.error_file':'/var/log/cherrypy/agendafest.log',
				 'request.show_tracebacks': False,
                                 },

	  '/media':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': MEDIA_DIR,
				},
	  '/':
				{'tools.caching.on': True,
				 'tools.caching.delay':3000,
				 'tools.proxy.on':True,
				 #mmmm... cookies
				 'tools.sessions.on': True,
				 'tools.sessions.storage_type': 'file',
				 'tools.sessions.storage_path': './sessions',
				 'tools.sessions.timeout':60,#in minutes
				 'tools.encode.on':True,
				 'tools.encode.encoding':'utf8',
				 'enviroment':'production',
				 'log.error_file':'/var/log/cherrypy/agendafest.log'
 				}
	    }

def merge(username, festname, alpha = 0.96, beta = 0.04, retDict = False, logzzz=True):
	"""
	merges the buzzzz scores and the similarities, with an optional log scaling for the buzz
	returns a list of tuples by default can also return a dict
	"""
	from_last = lfm_artists(username)
	if len(from_last['top_artists']) == 0:
		from_last =	 lfm_artists(username, period = 'overall')
	userartists =  [art[0] for art in from_last['top_artists']]
	#print userartists
	from_fest = festy(festname)
	festartists = [art['name'] for art in from_fest['response']['entities']]
	#print festartists
	lt = likeThis(festartists, userartists)
	lt.run()
	max_buzzzz = from_fest['response']['entities'][0]['ordering']['value'] # list is sorted so this is max
	min_buzzzz = from_fest['response']['entities'][-1]['ordering']['value']# and thus this is the min 
	print 'max_buzzzz:', max_buzzzz, 'min_buzzzz', min_buzzzz
	if min_buzzzz > 0:
		min_buzzzz = 0 # if nothing is negative, no need to adjust
	if retDict:
		merged_list = {}
	else:
		merged_list = []
	for art in from_fest['response']['entities']:
		try:
	                if logzzz:
				adjusted_buzzzz = math.log1p((abs(min_buzzzz)+art['ordering']['value'])/\
                                                             float(abs(min_buzzzz)+max_buzzzz))
				print "buzzzz:", art['ordering']['value'], "adjusted:",adjusted_buzzzz
			else:
				adjusted_buzzzz = (abs(min_buzzzz)+art['ordering']['value'])/\
                                              float(abs(min_buzzzz)+max_buzzzz)

			if retDict:
				merged_list[art['name']]=((alpha*lt.result[art['name']][0]) + \
					  (beta*adjusted_buzzzz), lt.result[art['name']][1])
				print "artist: {artist} buzzzz is {buzzzz}, sim is {sim}, merge is {merge}".format(\
					artist=art['name'], buzzzz=adjusted_buzzzz,
					   sim=lt.result[art['name']][0], merge=merged_list[art['name']])
			else:
				merged_list.append((art['name'], 
					(alpha*lt.result[art['name']][0]) +
					 (beta*adjusted_buzzzz), lt.result[art['name']][1]))
			        print "artist: {artist} buzzzz is {buzzzz}, sim is {sim}, merge is {merge}".format(\
					artist=art['name'], buzzzz=adjusted_buzzzz,
                                           sim=lt.result[art['name']][0], merge=merged_list[-1][1])
		except Exception, e:
			print 'trouble dealing with '+ str(art), 'reason:', e
	if not retDict:
		merged_list.sort(key=lambda x:x[1], reverse=True)
	return merged_list

def lfm_artists(username, cutoff=20, period = '12month'):
	net = pylast.get_lastfm_network(LAST_KEY, LAST_SECRET)
	user = pylast.User(username, net)
	artists = user.get_top_artists(period=period)
	return {'username':user.get_name(),
			'top_artists':\
			map(lambda artist:(artist.item.name, artist.weight), artists[:20])}
			
def festy(festname):
	return simplejson.loads(urllib2.urlopen('http://apib2.semetric.com/chart/{fest}?token={key}'.format(fest=fest2uuid[festname], 
																						key=MM_KEY)).read())
#def open_page():
#	webbrowser.open("http://127.0.0.1:8080/")
#cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(AgendafestApi(), '/', config=config)
cherrypy.engine.start()
