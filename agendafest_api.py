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
import urllib2

import pylast

from likeThis import *
from sonar_times import *
from credentials import *

MEDIA_DIR = os.path.join(os.path.abspath("."), u"media")

fest2uuid = {'greenman' : '21c7356b82b04771966b08c122543064',
			'Womad' : '673139f25d684e718709ea51299ccf05',
			'downloadfestival' : '8020e8c93a5d4c19a913e253c44f2e8f',
			'bestival' : '97aa4ce95e92412ca914300526a3cc99',
			'sonar' : 'a374b1e3bbfa4107890b56ed74c7e7fe',
			'glastonbury' : 'b16a75d1be374a0485da7f987deb841f',
			'hopfarm' : 'e2456c5842294759a54d3c9409af0755',
			'fleadh' : 'f1b0e90e837d4144ac9760efd7024b08',
			'leedsreading' : 'f6fbc6cacccc44acbe495aede3aad112',
			'standoncalling' : 'fecca33180824101a75d6cbc30e772ff'}


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

config = {'/media':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': MEDIA_DIR,
				}
		}

def merge(username, festname, alpha = 0.5, beta = 0.5):
	from_last = lfm_artists(username)
	if len(from_last['top_artists']) == 0:
		from_last =  lfm_artists(username, period = 'overall')
	userartists =  [art[0] for art in from_last['top_artists']]
	print userartists
	from_fest = festy(festname)
	festartists = [art['name'] for art in from_fest['response']['entities']]
	print festartists
	lt = likeThis(festartists, userartists)
	lt.run()
	max_buzzzz = from_fest['response']['entities'][0]['ordering']['value'] # list is sorted so this is max
	merged_list = []
	for art in from_fest['response']['entities']:
		try:
			merged_list.append((art['name'], 
					(alpha*lt.result[art['name']][0]) + ((beta*art['ordering']['value'])/max_buzzzz), 
					lt.result[art['name']][1]))
		except Exception, e:
			print 'trouble dealing with '+ str(art), 'reason:', e
	print merged_list
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
def open_page():
	webbrowser.open("http://127.0.0.1:8080/")
# cherrypy.engine.subscribe('start', open_page)
cherrypy.tree.mount(AgendafestApi(), '/', config=config)
cherrypy.engine.start()
