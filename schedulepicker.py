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


test_sonar = [("16/06/11","12.00","Sonar Village","Ragul","698630"),
("16/06/11","13.30","Sonar Village","Half Nelson + Vidal Romero","?"),
("16/06/11","15.00","Sonar Village","Toro y Moi","529386"),
("16/06/11","16.00","Sonar Village","Floating Points","517772"),
("16/06/11","15.30","Sonar Village","Little Dragon","179949"),
("16/06/11","18.30","Sonar Village","Shuttle ","557378"),
("16/06/11","19.30","Sonar Village","Dels","604272"),
("16/06/11","20.15","Sonar Village","Offshore","104772"),
("16/06/11","21.15","Sonar Village","Eskmo","200472"),
("16/06/11","12.00","SonarDôme","Nino","698638"),
("16/06/11","13.00","SonarDôme","Pai Mei","698635"),
("16/06/11","14.00","SonarDôme","Hiroaki","698636"),
("16/06/11","15.00","SonarDôme","AEIOU","89504"),
("16/06/11","16.00","SonarDôme","Poirier feat. Boogat","?"),
("16/06/11","17.15","SonarDôme","Kidkanevil","485934"),
("16/06/11","18.30","SonarDôme","The Brandt Brauer Frick Ensemble","698644"),
("16/06/11","19.30","SonarDôme","San Soda","466878"),
("16/06/11","20.45","SonarDôme","Julian Gomes","698631")]

test_dict = {"Ragul":(0.44902255350039738, u'Noisia'),
"Half Nelson + Vidal Romero":(0.84902255350039738, u'Noisia'),
"Toro y Moi":(0.4490225536039738, u'Noisia'),
"Floating Points":(0.4498255350039738, u'Noisia'),
"Little Dragon":(0.4495255350039738, u'Noisia'),
"Shuttle":(0.4490225900039738, u'Noisia'),
"Dels":(0.4490225538039738, u'Noisia'),
"Offshore":(0.45902255350039738, u'Noisia'),
"Eskmo":(0.74902255350039738, u'Noisia'),
"Nino":(0.54902255350039738, u'Noisia'),
"Pai Mei":(0.24902255350039738, u'Noisia'),
"Hiroaki":(0.94902255350039738, u'Noisia'),
"AEIOU":(0.44902255350039738, u'Noisia'),
"Poirier feat. Boogat":(0.34902255350039738, u'Noisia'),
"Kidkanevil":(0.74902255350039738, u'Noisia'),
"The Brandt Brauer Frick Ensemble":(0.14902255350039738, u'Noisia'),
"San Soda":(0.64902255350039738, u'Noisia'),
"Julian Gomes":(0.24902255350039738, u'Noisia'),
}
class schedulepicker:
	def __init__(self, rankdict, schedule = test_sonar, step=15):
		self.schedule = schedule
		self.rankdict = rankdict
		self.step = step
		
	def _fill_slot(self):
		playing_now = []
		for date, time, venue, artist, mm_id in self.schedule:
			nexttime, nextdate = add_some_minutes(self.currenttime, self.currentdate, self.step) 
			nexthours, nextminutes = map(int, nexttime.split('.'))
			nextT = float(nexthours)+(float(nextminutes)/60)
			thishours, thisminutes = map(int, time.split('.'))
			thisT = float(thishours)+(float(thisminutes)/60)
			if time >= self.currenttime and (thisT < nextT) and date == self.currentdate:
				playing_now.append((date, time, venue, artist, mm_id))
		print "playing_now:", playing_now
		winner = None
		min_dist = 10000
		for date, time, venue, artist, mm_id in playing_now:
			try:
				print "dist:", self.rankdict[artist][0]
				if self.rankdict[artist][0] < min_dist:
					min_dist = self.rankdict[artist][0]
					winner = date, time, venue, artist, self.rankdict[artist][0], self.rankdict[artist][1]
			except:
				print "can't find", artist, "moving on..."
				continue
		return winner
				
		
	def build_cal(self):
		#assumes self.schedule[0] is earliest and self.schedule[-1] is the last
		print self.schedule
		self.currenttime = self.schedule[0][1]
		self.currentdate = self.schedule[0][0]
		self.agenda = []
		currently_at = None
		print "date:", self.currentdate, "time:", self.currenttime
		print self.schedule[-1][1]
		print self.currenttime <= self.schedule[-1][1]
		while (self.currentdate != self.schedule[-1][0] or self.currenttime <= self.schedule[-1][1]):
			print "start:", self.schedule[0][1], self.schedule[0][0]
			print "end:",  self.schedule[-1][1], self.schedule[-1][0]
			print "hello at :", self.currenttime, self.currentdate
			print "over time:", self.currentdate != self.schedule[-1][0]
			print "over date:", 
			picked = self._fill_slot()
			if picked != currently_at:
				self.agenda.append(picked)
				print "adding", picked
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
	sp = schedulepicker(test_dict, test_sonar)
	sp.build_cal()
	print "test schedule:", sp.agenda
