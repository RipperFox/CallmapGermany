#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# By Ulrich Thiel, VK2UTL/DK1UT
import sys  
import sqlite3
import csv
from sets import Set

reload(sys)  
sys.setdefaultencoding('utf8')

dbconn = sqlite3.connect('calls.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
dbconn.row_factory = dict_factory
dbcursor = dbconn.cursor()

dbcursor.execute("SELECT Street, Zip FROM Locations WHERE Geocode = 1")
res = dbcursor.fetchall()

counter = 0
with open('calls.csv', 'w') as csvfile:
    fieldnames = ['Lng', 'Lat', 'Label', 'Marker']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    
    for row in res:
    	street = row['Street']
    	zip = row['Zip']
    	query = "SELECT Call, Class, Name, Street, Zip, City, Lng, Lat FROM CallsComplete WHERE Street=\"%s\" AND Zip=\"%s\"" % (street, zip)
    	dbcursor.execute(query)
    	res = dbcursor.fetchall()
    	label = "<div class='googft-info-window'>"
    	classes = Set([])
    	
    	for i in range(0,len(res)):
    		counter = counter + 1
    		current = res[i]
    		classes.add(current['Class'])
    		label = label + "<b>"+current['Call']+" ("+current['Name']+")</b><br>"
    		label = label + current['Street'] + ", " + current['Zip'] + " " + current['City']
    		if i < len(res)-1:
    			label = label + "<br><br>"
    		
    	if classes == Set(["A","E"]):
    		marker = "small_blue"
    	elif classes == Set(["A"]):
    		marker = "small_red"
    	elif classes == Set(["E"]):
    		marker = "small_purple"
    		
    	label = label + "</div>"
    	lat = current['Lat']
    	lng = current['Lng']

    
    	writer.writerow({'Lng':lng,'Lat':lat, 'Label':label, 'Marker':marker})

print counter

dbconn.close()