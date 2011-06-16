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
		
	def run(self):
		if self.method == 'last':
			self.last()
		else:
			raise NotImplementedError
		
	def last(self):
		network = pylast.get_lastfm_network(LAST_KEY, LAST_SECRET)
		self.ref_tags = defaultdict(float)
		for artist in self.against:
			print 'querying', artist
			for tag in pylast.Artist(artist, network).get_top_tags():
				self.ref_tags[tag.item] += float(int(tag.weight)+1)/len(self.against)
		# print self.ref_tags
		flatTags = map(lambda tag: (tag[0], int(tag[1]+1)), self.ref_tags.items())
		# print sorted(flatTags, key=lambda x: x[1], reverse = True)
		
		aDict = corpora.Dictionary()
		# aDict.bow2bow()
			
			


class untitledTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	# unittest.main()
	lt = likeThis([], ['lady gaga', 'ke$ha', 'rihanna'])
	lt.run()