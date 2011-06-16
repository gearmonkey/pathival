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

from gensim import corpora, models, similarities
import pylast


from credentials import *

class likeThis:
	"""
	builds a similarity score of all the artists in one list against the artists in the other.

	default similarity engine is last.fm, other things later
	"""
	def __init__(self, compare, against, method='last'):
		self.compare = compare
		self.against = against
		self.method = method
		self.result = []
		
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
			for tag in pylast.Artist(artist, network).get_top_tags():
				self.ref_tags[tag.item.name] += float(int(tag.weight)+1)/len(self.against)
				refdict[tag.item.name]=int(tag.weight)+1
			refbows.append(self._tags2bow(refdict))
	
		target_tags = self._tags2bow(self.ref_tags)
		
		resultlist = []
		for artist in self.compare:
			if artist in self.against:
				self.result.append((artist, 1, artist))
				continue
			artdict = {}
			for tag in pylast.Artist(artist, network).get_top_tags():
				artdict[tag.item.name]=int(tag.weight)+1
			this_bow = self._tags2bow(artdict)
			sms = similarities.Similarity([target_tags, this_bow])
			ref_sms = similarities.Similarity([this_bow]+refbows)
			min_dist = [None, 10000]
			for idx, distance in enumerate(list(ref_sms)[0][1:]):
				if distance < min_dist[1]:
					min_dist[1] = distance
					min_dist[0] = self.against[idx]
			self.result.append((artist, list(sms)[0][1], min_dist[0]))
		
		
			
			
def expand(tagList):
	'''dirty dirty hack to unwind a bag of words. terrible.'''
	reallyFlat = ""
	for word, times in tagList:
		for i in range(times):
			reallyFlat += " "+word
	return reallyFlat
class untitledTests(unittest.TestCase):
	def setUp(self):
		pass
		



if __name__ == '__main__':
	# unittest.main()
	lt = likeThis(['katy perry', 'pfm', 'aphex twin', 'fintroll', 'robyn', 'lady gaga'], ['lady gaga', 'ke$ha', 'rihanna'])
	lt.run()
	print lt.result