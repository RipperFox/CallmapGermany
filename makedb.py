#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# By Ulrich Thiel, VK2UTL/DK1UT
# Reads calls.txt and creates calls.db


##############################################################################
# Imports
import re
import sqlite3
import sys
import io # for open with encoding support

##############################################################################
# Default encoding
reload(sys)
sys.setdefaultencoding('utf-8')


##############################################################################
# Fixing characters and umlauts, remove garbage
def fix(str):
	str = re.sub("u\"", "ü", str)
	str = re.sub("o\"", "ö", str)
	str = re.sub("a\"", "ä", str)
	str = re.sub("A\"", "Ä", str)
	str = re.sub("U\"", "Ü", str)
	str = re.sub("O\"", "Ö", str)
	str = re.sub("\"", "", str)
	str = re.sub("\n", "", str)
	str = re.sub("\f", "", str)
	str = re.sub("Seite [0-9]{1,3}", "", str)
	str = re.sub("[1-6][\s]*Liste der.*Klubstation", "", str)
	return str
	
##############################################################################
# Fixing city names
def fixCity(str):
	#insert dash
	pos = re.search("[a-z][A-Z]",str)
	if pos == None: 
		return str	
	else:
		pos = pos.start()
		return str[0:pos+1]+"-"+str[pos+1:]

##############################################################################
# Main program

# Read date from callbook
callbookdate = None
with open('calls.txt') as f:
	for line in f:
		line = unicode(line, 'utf-8')
		if re.match("vom [0-9]{1,2}\. (Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)", line):
			line = re.sub("vom[ ]*", "", line)
			callbookdate = line
			break
			
if callbookdate != None:
	callbookdatesplit = callbookdate.split(" ")
	callbookmonth = ""
	if callbookdatesplit[1] == "Januar":
		callbookmonth = "01."
	elif callbookdatesplit[1] == "Februar":
		callbookmonth = "02."
	elif callbookdatesplit[1] == "März":
		callbookmonth = "03."
	elif callbookdatesplit[1] == "April":
		callbookmonth = "04."
	elif callbookdatesplit[1] == "Mai":
		callbookmonth = "05."
	elif callbookdatesplit[1] == "Juni":
		callbookmonth = "06."
	elif callbookdatesplit[1] == "Juli":
		callbookmonth = "07."
	elif callbookdatesplit[1] == "August":
		callbookmonth = "08."
	elif callbookdatesplit[1] == "September":
		callbookmonth = "09."
	elif callbookdatesplit[1] == "Oktober":
		callbookmonth = "10."
	elif callbookdatesplit[1] == "November":
		callbookmonth = "11."
	elif callbookdatesplit[1] == "Dezember":
		callbookmonth = "12."

	callbookdate = callbookdatesplit[0]+callbookmonth+callbookdatesplit[2]
	callbookdate = re.sub("\n", "", callbookdate)
	
print "Callbook date: " + str(callbookdate)

# Read file and extract call records
calls = [] #will be the array of call records
call = ""	#for reading lines
with io.open('calls.txt', encoding='ISO-8859-1') as f:
	for line in f:		
		
		# start with fixing string
		# form feed character at line beginning yields regexp failure for unknown reason (reported)
        	#line = unicode(line.decode('latin-1'), 'utf-8')
        	#line = unicode(line, 'utf-8')
		line = fix(line)
		
		if line == "":
			continue
		
		#match call sign		
		if re.match("D[A-R][0-9][A-Z]+", line): #match call sign
			if call != "":
				calls.append(call)
				call = ""
			call = line
		else:
			call = call + " " + line	#insert whitespace in case of newline in between 

#flush
calls.append(fix(call)) 

#now process data
#this is not perfect but it works
callsprocessed = []	
for call in calls:
	fields = call.split(";")
	callsign = fields[0].split(",")[0]
	callclass = fields[0].split(",")[1]
	name = fields[0].split(",")[2]
	name = re.sub("^[\s]*", "", name)
	name = re.sub("[\s]*$", "", name)
	callclass = re.sub("^[\s]*", "", callclass)
	if len(fields) == 1:	#no address given

		callsprocessed.append({'Call': callsign, 'Class': callclass, 'Category':None, 'Name': name, 'Street':None, 'Zip':None, 'City':None, 'Date':callbookdate})
	else:
		if len(fields) == 3:	#one address given
			street = fields[1]
			street = re.sub("^[\s]*", "", street)
			street = re.sub("[\s]*$", "", street)
			street = re.sub(r"(\w)([A-Z])", r"\1-\2", street)	#by salat
			city = fields[2].split(",")[0]	#just in case, there are some errors in the PDF eg DB0ATV
			city = re.sub("^[\s]*", "", city)
			city = re.sub("[\s]*$", "", city)
			zip = city[0:5]
			city = city[6:]
			city = fixCity(city)
			
			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Category':None, 'Name': name, 'Street':street, 'Zip':zip, 'City':city, 'Date':callbookdate})
			
		elif len(fields) == 4:	#two addresses given
			street1 = fields[1]
			street1 = re.sub("^[\s]*", "", street1)
			street1 = re.sub("[\s]*$", "", street1)
			city1 = fields[2].split(",")[0]
			street2 = fields[2].split(",")[1]
			city2 = fields[3]
			street1 = re.sub("^[\s]*", "", street1)
			street1 = re.sub("[\s]*$", "", street1)
			street1 = re.sub(r"(\w)([A-Z])", r"\1-\2", street1) #by salat
			city1 = re.sub("^[\s]*", "", city1)
			city1 = re.sub("[\s]*$", "", city1)
			zip1 = city1[0:5]
			city1 = city1[6:]
			street2 = re.sub("^[\s]*", "", street2)
			street2 = re.sub("[\s]*$", "", street2)
			street2 = re.sub(r"(\w)([A-Z])", r"\1-\2", street2)	#by salat
			city2 = re.sub("^[\s]*", "", city2)
			city2 = re.sub("[\s]*$", "", city2)
			zip2 = city2[0:5]
			city2 = city2[6:]
			city1 = fixCity(city1)
			city2 = fixCity(city2)

			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Category':None, 'Name': name, 'Street':street1, 'Zip':zip1, 'City':city1, 'Date':callbookdate})
			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Category':None, 'Name': name, 'Street':street2, 'Zip':zip2, 'City':city2, 'Date':callbookdate})
	
print "Records: " + str(len(callsprocessed))

#now, add data to database 
dbconn = sqlite3.connect('calls.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
dbconn.row_factory = dict_factory
dbcursor = dbconn.cursor()

#update table
#first, add locations
for call in callsprocessed:
	if call['Street'] == None:
		continue
	location = {'Street':call['Street'], 'Zip':call['Zip'], 'City':call['City']}
	columns = ', '.join(location)
	placeholders = ', '.join('?' * len(location))
	sql = 'INSERT INTO Locations ({}) VALUES ({})'.format(columns, placeholders)
	dbcursor.execute(sql, location.values())

dbconn.commit()

#now, reset recreate call db
dbcursor.execute("DELETE FROM Calls")
dbconn.commit()

for call in callsprocessed:
	
	if call['Street'] != None:
		res = dbcursor.execute("SELECT Id FROM Locations WHERE Street=\""+call['Street']+"\" AND Zip=\""+call['Zip']+"\" AND City=\""+call['City']+"\"").fetchone()
		locationid = res['Id']
	else:
		locationid = None
		
	calldata = {'Call':call['Call'], 'Class':call['Class'], 'Category':call['Category'], 'Name':call['Name'], 'Date':call['Date'], 'Location':locationid}
	
	columns = ', '.join(calldata.keys())
	placeholders = ', '.join('?' * len(calldata))
	sql = 'INSERT INTO Calls ({}) VALUES ({})'.format(columns, placeholders)
	dbcursor.execute(sql, calldata.values())
	
#cleanup and commit
dbcursor.execute("VACUUM")			
dbconn.commit()
dbconn.close()