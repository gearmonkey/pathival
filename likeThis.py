#!/usr/bin/env python
# encoding: utf-8
"""
likeThis.py

builds a similarity score of all the artists in one list against the artists in the other.

default similarity engine is last.fm, other things later

Created by Benjamin Fields on 2011-06-16.
Copyright (c) 2011. All rights reserved.
"""

import sys
import os
import unittest
from collections import defaultdict

try:
	import cherrypy
except:
	print 'No cherrypy, so no tag pass through info'

from gensim import corpora, models, similarities
import pylast


from credentials import *

cached_tags = {}


class likeThis:
	"""
	builds a similarity score of all the artists in one list against the artists in the other.

	default similarity engine is last.fm, other things later
	"""
	def __init__(self, compare, against, method='last'):
		self.compare = compare
		self.against = against
		self.method = method
		self.result = {}
		
	def run(self):
		if self.method == 'last':
			self.last()
		else:
			raise NotImplementedError
		
	def _tags2bow(self, tagDict):
		flatTags = map(lambda tag: (tag[0], int(tag[1]+1)), tagDict.items())
		bow = self.aDict.doc2bow(expand(flatTags), allowUpdate = True)
		return bow
	
	def last(self):
		network = pylast.get_lastfm_network(LAST_KEY, LAST_SECRET)
		self.ref_tags = defaultdict(float)
		refbows = []
		refdict = {}
		self.aDict = corpora.Dictionary()
		for artist in self.against:
			print 'querying', artist
			try:
				try:
					artist_tags = cached_tags[artist]
					print '\tfound cache!'
				except KeyError:
					print '\tno cache...'
					cached_tags[artist] = pylast.Artist(artist, network).get_top_tags()
					artist_tags = cached_tags[artist]
				for tag in artist_tags:
					self.ref_tags[tag.item.name] += float(int(tag.weight)+1)/len(self.against)
					refdict[tag.item.name]=int(tag.weight)+1
				refbows.append(self._tags2bow(refdict))
			except:
				print 'fell over on this artist, moving on...'
				continue
	
		target_tags = self._tags2bow(self.ref_tags)
		
		resultlist = []
		for artist in self.compare:
			if artist in self.against:
				self.result[artist] = (1, artist)
				continue
			artdict = {}
			try:
				print 'querying', artist
				try:
					artist_tags = cached_tags[artist]
					print '\tfound cache!'
				except KeyError:
                                        print '\tno cache...'
                                        cached_tags[artist] = pylast.Artist(artist, network).get_top_tags()
					artist_tags = cached_tags[artist]
				for tag in artist_tags:
					artdict[tag.item.name]=int(tag.weight)+1
			except:
				print 'last.fm doesn\'t know about', artist, 'moving on...'
				continue
			this_bow = self._tags2bow(artdict)
			sms = similarities.Similarity([target_tags, this_bow])
			ref_sms = similarities.Similarity([this_bow]+refbows)
			max_sim = [None, -1]
			for idx, distance in enumerate(list(ref_sms)[0][1:]):
				if distance > max_sim[1]:
					max_sim[1] = distance
					max_sim[0] = self.against[idx]
			best_dim = [-1, float('inf'), 0]#that is: idx, dim diff, mean magnitude
			match_bow_dict = dict(refbows[self.against.index(max_sim[0])])
			for tag_id, tag_mag in this_bow:
				try:
					ref_mag = match_bow_dict[tag_id]
					diff = abs(ref_mag-tag_mag)
					avg = (ref_mag+tag_mag)/2.0
					if diff == 0:
						#here only test mean mag
						if avg > best_dim[2]:
							best_dim = [tag_id, 0.00000000001, avg]
					elif ((1/diff) + (avg/100)) > ((1/best_dim[1]) + (best_dim[2]/100)):
						best_dim = [tag_id, diff, avg]
				except KeyError:
					continue
			print best_dim
			print self.aDict
			try:
				print 'best dim:', str(self.aDict[best_dim[0]])
			except KeyError:
				print 'best dim unknown'
			print '\tdiff:', best_dim[1], 'mean mag:', best_dim[2]
			self.result[artist] = (list(sms)[0][1], max_sim[0])
			try:
				if best_dim[0] == -1:
					reason = 'who knows'
				else:
					reason = self.aDict[best_dim[0]]
				cherrypy.session[artist] = (self.result[artist], reason)
				print artist, 'provenance to', self.result[artist], 'by', 
				print reason, 'in session'
			except:
				print 'failed to attach the provanace of',artist, 'to the session'
				
			
def expand(tagList):
	'''dirty dirty hack to unwind a bag of words. terrible.'''
	reallyFlat = []
	for word, times in tagList:
		for i in range(times):
			reallyFlat += [word]
	return reallyFlat
class untitledTests(unittest.TestCase):
	def setUp(self):
		pass
		



if __name__ == '__main__':
	# unittest.main()
	lt = likeThis(['katy perry', 'pfm', 'aphex twin', 'fintroll', 'robyn', 'lady gaga'], ['lady gaga', 'ke$ha', 'rihanna'])
	lt.run()
	print lt.result
