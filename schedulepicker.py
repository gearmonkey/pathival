#!/usr/bin/env python
# encoding: utf-8
"""
schedulepicker.py

Created by Benjamin Fields on 2011-06-17.
Copyright (c) 2011 . All rights reserved.
"""

import sys
import os
import unittest
import datetime
import copy

from sonar_times import *


class schedulepicker:
	def __init__(self, rankdict, schedule = sonar, step=15):
		self.schedule = copy.deepcopy(schedule)
		self.rankdict = rankdict
		self.step = step
		
	def _fill_slot(self):
		playing_now = []
		for date, time, venue, artist, mm_id in self.schedule:
			if time >= self.currenttime and (time < self.currenttime+self.step) and date == self.currentdate:
				playing_now.append((date, time, venue, artist, mm_id))
		winner = None
		min_dist = 10000
		for date, time, venue, artist, mm_id in playing_now:
			if self.rankdict[artist][0] < min_dist:
				min_dist = self.rankdict[artist][0]
				winner = date, time, venue, artist, self.rankdict[artist][0], self.rankdict[artist][1] 
		return winner
				
		
	def build_cal(self):
		#assumes self.schedule[0] is earliest and self.schedule[-1] is the last
		self.currenttime = self.schedule[0][1]
		self.currentdate = self.schedule[0][0]
		self.schedule = []
		currently_at = None
		while (self.currentdate != self.schedule[-1][0] and self.currenttime <= self.schedule[-1][1]):
			picked = _fill_slot()
			if picked != currently_at:
				self.schedule.append(picked)
				currently_at = picked
			self.currenttime , self.currentdate = add_some_minutes(self.currenttime, self.currentdate, self.step) 
		return

def add_some_minutes(time, date, thismany):
	"""this doesn't deal with month transitions
	"""
	hours, minutes = map(int, time.split('.'))
	day, month, year = map(int, date.split("/"))
	
	minutes += thismany
	if minutes > 59:
		minutes %= 60
		hours +=1
	if hours > 23:
		hours %=24
		day += 1
	
	return str(hours)+'.'+str(minutes), str(day)+'/'+str(month)+'/'+str(year)

class schedulepickerTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	pass