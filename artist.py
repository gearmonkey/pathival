#!/usr/bin/env python
# encoding: utf-8
"""
artist.py

Created by Gregory Mead on 2011-06-16.
MusicHackDay Barcelona 2011
"""

import logging
#import sparkplot
import urllib2
#from simplejson import loads
import sys
import os
import urllib
import urllib2
import demjson as json

from keys import *


#class Sparkweb(sparkplot.Sparkplot):
#	def get_input_data(self, dataset_name, LFID):
#		"""
#		assembles and fetches data from a musicmetric timeseries datasource
#		then formats the result for ploting timeseries
#		"""
#		raw_response = loads(urllib2.urlopen(base_url+'/artist/lastfm:'+LFID+'/'+dataset_name+'?token='+MM_KEY).read())
#		self.data = raw_response['response']['data']


#def make_spark(artist):
#	dataset_name = "fans/myspace"
#	LFID = urllib.quote(artist.encode('utf-8'))
#	sparker = Sparkweb()
#	sparker.get_input_data(dataset_name, LFID)
#	sparker.process_args()
#	sparker.plot_sparkline()
#	return 0


def get_description(artist_name):
	"""Grabs a bunch of info about the band from Seevl (or last.fm for description if there isn't 
	   one on seevl). Returns a triple: 	
	   ("Description Text", "Genre", [("link_type", "link_url]),..,("link_type", "link_url)] )"""
	#Setup the variables incase everything fails
	artist_description = "We don't have a description or bio for this band, sorry :("
	genre = "Unknown"
	url_list = []	
	try:
		#Set up the headers etc for Seevl.net API and request artist infos
		url = 'http://data.seevl.net/entity/?prefLabel={name}'.format(name=urllib.quote(artist_name))
		headers = { 'Accept' : 'application/json',
		            'X_APP_ID' : SV_ID,
		            'X_APP_KEY' : SV_KEY }
		req = urllib2.Request(url, None, headers)
		response = urllib2.urlopen(req)
		artist_page = response.read()
		artist_info = json.decode(artist_page) #This is a dict with a load of seevl info about artist
		#If seevl doesen't have a description then look for it on last.fm to see if they have one:
		if len(artist_info['results']) == 0:
			try:
				lfm_url = "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist}&api_key={key}&format=json".format(artist=urllib.quote(artist_name), key=LF_KEY)
				lfm_info = json.decode(urllib2.urlopen(lfm_url).read())
				artist_description = "{text}   {attrib}".format(text=lfm_info['artist']['bio']['summary'].encode('utf-8'), attrib="Description from last.fm")
				lfm_description = True
				#Grab the genre off last.fm too if Seevl doesen't have it
				tag_url = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={artist}&api_key={key}&format=json".format(artist=urllib.quote(artist_name).encode('utf-8'), key=LF_KEY)
				tag_data = json.decode(urllib2.urlopen(tag_url).read())
				genre = tag_data['toptags']['tag'][0]['name'].title()
			except Exception, e: #Fun error handling
				print "Error", e
		else:
			#If Seevl has info on the artist, grab some facts about them too
			artist_id = artist_info['results'][0]['id']
			artist_id
			fact_url = 'http://data.seevl.net/entity/{entity}/facts'.format(entity=artist_id)		
			req_fact = urllib2.Request(fact_url, None, headers)
			response = urllib2.urlopen(req_fact)
			fact_page = response.read()
			artist_facts = None
			artist_facts = json.decode(fact_page)
			if artist_facts.has_key('genre'):
				genre = artist_facts['genre'][0]['prefLabel'].replace(" music", "").encode('utf-8') #Grab the genre from Seevl
			if artist_info['results'][0].has_key('description'):
				artist_description = "{text}   {attrib}".format(text=artist_info['results'][0]['description'].encode('utf-8'), attrib="Summary from Seevl.net")
				artist_description = artist_description.replace("<strong>", "").replace("</strong>", "").replace("<p>", "").replace("</p>", "")
			elif lfm_description is not True:
				#If we still don't have a description for the artist, then try build one using some facts
				artist_start = 'some year (assuming they exist)'
				artist_end = -1
				artist_genre = "probably some genre that might exist if the band exists"
				if artist_facts is not None:
					if artist_facts.has_key('activity_start'):
						artist_start = artist_facts['activity_start'][0]['value']
					if artist_facts.has_key('activity_end'):
						artist_end = artist_facts['activity_end'][0]['value']
				artist_description = "{a} have been active since {s}. Their music is {g}\n".format(a=artist_name.encode('utf-8'), s=artist_start, g=genre)
			#Grab the artist links from Seevl API, like: socialnet, website etc.	
			links_url = "http://data.seevl.net/entity/{entity}/links".format(entity=artist_id)
			req_links = urllib2.Request(links_url, None, headers)
			response = urllib2.urlopen(req_links)
			link_data = json.decode(response.read())
			for key, value in link_data.items():
				if key in ['wikipedia', 'nytimes', 'musicbrainz', 'homepage']:
					url_list.append((key.title(), value[0]))
		return (artist_description, genre, url_list)	
	except Exception, e:
		print e
		return (artist_description, genre, url_list)


def get_image(artist_name):
	"""Grabs the image URL's from last.fm and return the url for the most popular one
	   based on votes"""
	artist_name = urllib.quote(artist_name)
	url = "http://ws.audioscrobbler.com/2.0/?method=artist.getimages&artist={name}&api_key={key}&format=json".format(name=artist_name, key=LF_KEY)
	imurl = None
	try:
		imlist = []
		ph = urllib2.urlopen(url)
		page = ph.read()
		im = json.decode(page)
		for image in im['images']['image']:
			for item in image['sizes']['size']:
				if int(item['width']) == 126:
					url = item['#text']
					score = int(image['votes']['thumbsup']) - int(image['votes']['thumbsdown'])
					imlist.append([url, score])
		imlist.sort(key=lambda x: x[1], reverse=True)	
		imurl = imlist[0][0]
		imurl = imurl.replace("serve/126", "serve/126s")
		return imurl
	except Exception, e:
		print e
		return None


def get_preview(artist):
	"""Grabs the preview clip URL from 7Digital for the top song of the artist"""
	try:
		top_song_url = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist={artist}&api_key={key}&format=json".format(artist=urllib.quote(artist), key=LF_KEY)
		song_json = json.decode(urllib2.urlopen(top_song_url).read())
		toptrack = song_json['toptracks']['track'][0]['name']
		en_url = "http://developer.echonest.com/api/v4/song/search?api_key=N6E4NIOVYMTHNDM8J&format=json&results=1&artist={artist}&title={track}&bucket=id:7digital&bucket=audio_summary&bucket=tracks".format(artist=urllib.quote(artist), track=urllib.quote(toptrack))	
		en_json = json.decode(urllib2.urlopen(en_url).read())
		return en_json['response']['songs'][0]['tracks'][0]['preview_url']
	except Exception, e:
		print "Error", e
		return None


def main():
	artist = "Boys Noize"
	print artist
	#make_spark(artist)
	info = get_description(artist)
	print info[0]              #Artist Description
	print info[1]              #Artist Genre
	print info[2]              #Artist Weblinks
	print get_image(artist)    #Image URL
	print get_preview(artist)  #Preview mp3 URL


if __name__ == '__main__':
	main()

