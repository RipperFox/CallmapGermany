#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#By Ulrich Thiel, VK2UTL/DK1UT, RipperFox
#Adds coordinates to calls.db

##############################################################################
# Imports
import sqlite3
import geocoder
import requests
import sys
import time
from tqdm import tqdm

import json
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

dbconn = sqlite3.connect('calls.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
dbconn.row_factory = dict_factory
dbcursor = dbconn.cursor()

#For initial geocoding
#dbcursor.execute("SELECT * FROM Locations WHERE Geocode IS NULL")

#For update geocoding
#dbcursor.execute("SELECT * FROM Locations WHERE Geocode = 0") 

# Only failed OSM Nominatim entries:
dbcursor.execute("SELECT * FROM Locations WHERE Geocode = 2") 

res = dbcursor.fetchall()
print str(len(res)) + " addresses selected for geocoding"

#keep session alive
with requests.Session() as session:
	for i in tqdm(range(len(res))):
		row = res[i]
		address = row['Street'] + ", " + row['Zip'] + " " + row['City'] 
		address = address.encode("utf-8")
		#print address


                file = urllib2.urlopen("http://photon.komoot.de/api/?q={0}".format(urllib2.quote((address))))
                jsondata = json.load(file)
                file.close()


                #print jsondata["features"][0]["geometry"]["coordinates"][0], jsondata["features"][0]["geometry"]["coordinates"][1]

                try:
                    place = jsondata["features"][0]["geometry"]["coordinates"]
                except IndexError:
                    place = None
                
                if (place is None or len(place) ==0):
                    #dbcursor.execute("UPDATE Callsigns SET Geocode = 0 WHERE Id = " + str(row[0])) 
                    # better don't change status
                    print address + " --- not found"
                else:
                    lon = str(jsondata["features"][0]["geometry"]["coordinates"][0])
                    lat = str(jsondata["features"][0]["geometry"]["coordinates"][1])
                    Id = str(row["Id"])
                    print Id + "  "+  address + "  " + lat, lon
                    query = "UPDATE Locations SET Lng = %s, Lat = %s, Geocode = 3  WHERE Id = %s" % (lon, lat, Id)
                    dbcursor.execute(query)
                    dbconn.commit()
		
dbconn.close()
