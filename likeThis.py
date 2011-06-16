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
		self.method()
		
	def last(self, ):


class untitledTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	unittest.main()