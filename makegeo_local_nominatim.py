#!/usr/bin/env python
# -*- coding: utf-8 -*-
#By Ulrich Thiel, VK2UTL/DK1UT

import sqlite3
import geopy
import requests
import progressbar
import sys
import time

import urllib2
from xml.dom import minidom


reload(sys)
sys.setdefaultencoding('utf-8')

dbconn = sqlite3.connect('calls.db')
dbcursor = dbconn.cursor()

#dbcursor.execute("SELECT * FROM Callsigns WHERE Geocode IS NULL AND Street IS NOT NULL")
dbcursor.execute("SELECT * FROM Callsigns WHERE (Geocode IS NULL OR Geocode <> 1) and Street IS NOT NULL")
res = dbcursor.fetchall()
bar = progressbar.ProgressBar(maxval=len(res))
print bar.maxval
count = 0
with requests.Session() as session:
	bar.start()
	for row in res:
		address = row[4] + ", " + row[5] + " " + row[6] + ", Germany"
		address = address.encode("utf-8")
		#print address
		file = urllib2.urlopen("http://192.168.1.249/nominatim/search.php?q={0}&format=xml&polygon=0&addressdetails=0".format(urllib2.quote((address))))
		xmldoc = minidom.parseString(file.read())
		file.close()
		#print xmldoc.firstChild.getAttribute("timestamp")

		place = xmldoc.getElementsByTagName("searchresults")[0].getElementsByTagName("place")
		if (place is None or len(place) ==0):
			dbcursor.execute("UPDATE Callsigns SET Geocode = 2 WHERE Id = " + str(row[0])) 
			print address + " --- not found"
		else:
			lat = place[0].getAttribute("lat")
			lon = place[0].getAttribute("lon")
			print address + "  " + lat, lon
			#dbcursor.execute("UPDATE Callsigns SET Lng = " + str(g.longitude) + ", Lat = " + str(g.latitude) + ", Geocode = 1 WHERE Id = " + str(row[0]))
			dbcursor.execute("UPDATE Callsigns SET Lng = %s , Lat = %s , Geocode = 1 WHERE Id = %s " & (str(lon), str(lat), str(row[0]) )
		
		dbconn.commit()
		count = count + 1
		bar.update(count)

dbconn.close()
